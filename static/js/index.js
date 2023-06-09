// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // TASK DATA
        tasks: [],
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
                app.vue.tasks.push({
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
                app.enumerate(app.vue.tasks);
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
            document.getElementById("journal_modal_title").innerHTML += today;
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

    // This contains all the methods.
    app.methods = {
        set_adding_task: app.set_adding_task,
        add_task: app.add_task,
        get_active_tasks: app.get_active_tasks,
        submit_task_reflection: app.submit_task_reflection,
        submit_journal_entry: app.submit_journal_entry,
        search: app.search,
        clear: app.clear,
        add_to_group: app.add_to_group,
        remove_from_group: app.remove_from_group
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
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code in it. 
init(app);
