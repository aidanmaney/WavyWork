// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // TASK DATA
        task_label: "",
        task_description: "",
        task_start_time: "",
        task_end_time: "",
        task_category: "",
        task_is_group: false,
        task_group_id: null,
        // END TASK DATA

        // GROUP DATA
        all_users: [],
        search_users: [],
        group_users: [],
        is_displaying_search: false,
        search_query: "",
        group_name: "",
        // END GROUP DATA

        // REFLECTION DATA
        active_tasks: [],
        reflection_modal_tasks: [],
        reflection_attentiveness: 1,
        reflection_emotion: 1,
        reflection_efficiency: 1,
        reflections_available: false,
        reflections_done: false,
        reflection_journal: "",
        // END REFLECTION DATA

        // TIMELINE DATA
        next_10_days: [],
        all_user_tasks: [],
        // END TIMELINE DATA

        // EXPANDED TASK VIEW DATA
        current_task: null,
        task_view_task_id: 0,
        task_view_subtasks: [],
        task_view_group_members: [],
        task_view_label: "",
        task_view_description: "",
        task_view_is_group: "",
        is_adding_subtask: false,
        new_subtask_description: "",
        // END EXPANDED TASK VIEW DATA
    };    
    
    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {Vue.set(e, '_idx', k++);});
        return a;
    };

    app.set_adding_task = function (state)  {
        let modal = document.getElementById("add_task_modal");
        if (state){
            modal.classList.add("is-active")
        } else {
            modal.classList.remove("is-active")
            app.clear_add_form()
        }
    };

    app.get_users = () => {
        axios.get(get_users_url).then( (res) => {
            app.vue.all_users = app.enumerate(res.data.all_users);
        });
    }

    app.clear_add_form = () => {
        app.vue.task_label = "";
        app.vue.task_description = "";
        app.vue.task_start_time = "";
        app.vue.task_end_time = "";
        app.vue.task_category = "";
        app.vue.task_is_group = false;
    }


    app.add_task = () => {
        let member_ids = null;
        if (app.vue.task_is_group) {
            member_ids = app.vue.group_users.map(({ id }) => id);
        }

        axios.post(add_task_url,
            {   label: app.vue.task_label,
                description: app.vue.task_description,
                categorization: app.vue.task_category,
                start_time: app.vue.task_start_time,
                end_time: app.vue.task_end_time,
                is_group: app.vue.task_is_group,
                group_name: app.vue.group_name,
                members: member_ids
            }).then(function (response) {
                app.vue.all_user_tasks.push({
                    id: response.data.id,
                    label: app.vue.task_label,
                    description: app.vue.task_description,
                    categorization: app.vue.task_category,
                    is_group: app.vue.task_is_group,
                    created_by: response.data.created_by,
                    start_time: app.vue.task_start_time,
                    end_time: app.vue.task_end_time,
                    group_id: response.data.group_id
                })
                app.apply_date_data_to_tasks(app.enumerate(app.vue.all_user_tasks));
                app.set_adding_task(false);
            })
    }; 

    app.spawn_next_reflection_modal = () => {
        if (app.vue.active_tasks.length > 0){
            app.vue.reflection_modal_tasks.push(app.vue.active_tasks[app.vue.active_tasks.length - 1]);
            app.vue.active_tasks.pop()
        } else {
            app.vue.reflections_done = true;
            app.vue.reflection_modal_tasks = [];
            let today = new Date().toLocaleDateString();
            document.getElementById("journal_modal").classList.add("is-active");
            document.getElementById("journal_modal_title").innerHTML = "Daily Reflection for " + today;
        }
    }

    app.get_active_tasks = () => {
        axios.get(get_active_tasks_url).then( (res) => {
            if (res.data.active_tasks.length <= 0){
                console.log("No active tasks");
                return;
            }
            app.vue.active_tasks = app.enumerate(res.data.active_tasks);
            app.spawn_next_reflection_modal();
        });
    }

    app.submit_task_reflection = (task_id) => {
        axios.post(submit_task_reflection_url, {
            task_id: task_id,
            attentiveness: app.vue.reflection_attentiveness,
            emotion: app.vue.reflection_emotion,
            efficiency: app.vue.reflection_efficiency
        }).then( (res) => {
            app.vue.reflection_attentiveness = 1;
            app.vue.reflection_emotion = 1;
            app.vue.reflection_efficiency = 1;
        });
    }

    app.set_group_member_status = (a) => {
        a.map((e) => {Vue.set(e, 'is_group_member', false);});
        return a
    }

    app.add_to_group = (idx) => {
        Vue.set(app.vue.all_users[idx], 'is_group_member', true);
        app.vue.group_users.push(app.vue.all_users[idx]);
    }

    app.remove_from_group = (idx) => {
        Vue.set(app.vue.all_users[idx], 'is_group_member', false);
        app.vue.group_users.pop(app.vue.all_users[idx]);
    }

    app.search = () => {
        app.vue.search_users = [];
        app.vue.is_displaying_search = true;

        if (app.vue.search_query == ""){
            app.vue.is_displaying_search = false;
            return;
        }

        for (u of app.vue.all_users){
            if (u.first_name.toLowerCase().startsWith(app.vue.search_query.toLowerCase())){
                app.vue.search_users.push(u)
            }
        }
    }

    app.clear = () => {
        app.vue.is_displaying_search = false;
        app.vue.search_query = "";
        return;
    }

    app.check_if_reflections_available = () => {
        let today = new Date();
        let time = today.getHours();
        console.log(time)
        axios.get(check_for_submitted_reflections_url).then( (res) => {
            if ((time >= 18 || time < 8) && res.data.todays_reflections.length <= 0) {
                app.vue.reflections_available = true;
            } else {
                app.vue.reflections_available = false;
            }
        })
    }

    app.submit_journal_entry = () => {
        axios.post(submit_journal_entry_url, {entry: app.vue.reflection_journal}).then( () => {
            app.vue.reflection_journal = "";
        })
    }

    app.toggle_subtask_complete = (t_idx) => {
        axios.post(toggle_subtask_complete_url, {subtask_id: app.vue.task_view_subtasks[t_idx].id}).then( () => {
            app.vue.task_view_subtasks[t_idx].is_complete = !app.vue.task_view_subtasks[t_idx].is_complete;
        });
    }


    app.toggle_task_complete = function (task_id) {
        console.log('BEFORE:', app.data.all_user_tasks);
        axios.post(toggle_task_complete_url,
            {
                task_id: task_id
            }).then(function () {
                // ind = app.data.all_user_tasks.findIndex(i => i.id == task_id);
                
                // app.data.all_user_tasks[ind]['is_complete'] = true;
                // app.data.all_user_tasks = app.data.all_user_tasks.filter(i => i.is_complete == false);

                // app.data.all_user_tasks = app.get_all_users_tasks();
                app.get_all_users_tasks();

                // app.data.all_user_tasks = app.apply_date_data_to_tasks(app.enumerate(app.data.all_user_tasks));
                console.log("AFTER:", app.data.all_user_tasks);
            });
    }

    app.add_subtask = () => {
        axios.post(add_new_subtask_url, {
            task_id: app.vue.task_view_task_id,
            description: app.vue.new_subtask_description
        }).then( (res) => {
            app.vue.task_view_subtasks.push({
                "id": res.data.id,
                "task_id": app.vue.task_view_task_id, 
                "description": app.vue.new_subtask_description,
                "is_complete": false
            });

            app.enumerate(app.vue.task_view_subtasks);
            app.vue.is_adding_subtask = false;
            app.vue.new_subtask_description = "";
        });
    }

    app.get_next_10_days = () => {
        let date = new Date();
        let format_date;
        for (let i = 0; i < 10; i++) {
            format_date = date.toDateString().slice(3, -5);
            app.vue.next_10_days.push(format_date)
            date.setDate(date.getDate() + 1);
        }
        console.log(app.vue.next_10_days);
    }

    app.days_between_dates = (d1, d2) => {
        return Math.round((d2.getTime() - d1.getTime()) / (1000 * 3600 * 24)) + 1;
    }

    app.apply_date_data_to_tasks = (all_tasks) => {
        date_info_for_tasks = []

        let days_between;
        let start_date;
        let end_date;
        let start_relative_to_today;
        let end_relative_to_today;
        let column_class;

        for (task of all_tasks) {
            start_date = new Date(task.start_time)
            end_date = new Date(task.end_time)
            today = new Date()
            days_between = app.days_between_dates(start_date, end_date)
            start_relative_to_today = app.days_between_dates(today, start_date)
            end_relative_to_today = app.days_between_dates(today, end_date)
            overflows_left = start_relative_to_today < 0 ? true : false
            overflows_right = end_relative_to_today > 10 ? true : false

            if (overflows_left && overflows_right) {
                column_class = "is-10"
            }
            else if (overflows_left) {
                column_class = "is-" + (end_relative_to_today + 1)
            }
            else if (overflows_right) {
                column_class = "is-" + ((days_between - start_relative_to_today) + 1)
            }
            else {
                column_class = "is-" + days_between
            }

            date_info_for_tasks.push({
                days_between: days_between,
                start_relative_to_today: start_relative_to_today >= 0 ? start_relative_to_today : 0,
                end_relative_to_today: end_relative_to_today,
                overflows_left: overflows_left,
                overflows_right: overflows_right,
                column_class: column_class
            });
        }

        let k = 0;
        all_tasks.map((e) => {Vue.set(e, 'date_data', date_info_for_tasks[k++]);})
        return all_tasks
    }

    app.get_all_users_tasks = () => {
        axios.get(get_all_users_tasks_url).then( (res) => {
            console.log("all tasks", res.data.all_users_tasks);
            app.vue.all_user_tasks = app.apply_date_data_to_tasks(app.enumerate(res.data.all_users_tasks))
        });
    }

    app.open_expanded_task_view = (t_idx) => {
        let expanded_task = app.vue.all_user_tasks[t_idx];
        app.vue.task_view_task_id = expanded_task.id
        app.vue.current_task = expanded_task;
        app.vue.task_view_label = expanded_task.label;
        app.vue.task_view_description = expanded_task.description;
        app.vue.task_view_is_group = expanded_task.is_group;
        app.vue.is_adding_subtask = false;

        axios.get(get_task_subtasks_url, {params: {task_id: expanded_task.id}}).then( (res) => {
            app.vue.task_view_subtasks = app.enumerate(res.data.subtasks);
            console.log(app.vue.task_view_subtasks)
        });

        if (expanded_task.is_group) {
            axios.get(get_group_members_url, {params: {group_id: expanded_task.group_id}}).then( (res) => {
                app.vue.task_view_group_members = res.data.group_members
            });
        }

        document.getElementById("expanded_task_view_modal").classList.add("is-active");
    }



    // This contains all the methods.
    app.methods = {
        set_adding_task: app.set_adding_task,
        add_task: app.add_task,
        toggle_task_complete: app.toggle_task_complete,
        get_active_tasks: app.get_active_tasks,
        submit_task_reflection: app.submit_task_reflection,
        submit_journal_entry: app.submit_journal_entry,
        search: app.search,
        clear: app.clear,
        add_to_group: app.add_to_group,
        remove_from_group: app.remove_from_group,
        toggle_subtask_complete: app.toggle_subtask_complete,
        add_subtask: app.add_subtask,
        open_expanded_task_view: app.open_expanded_task_view
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        app.get_users();
        app.check_if_reflections_available();
        app.get_next_10_days();
        app.get_all_users_tasks();
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code in it. 
init(app);
