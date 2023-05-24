// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Data for tasks
        tasks: [],
        is_adding_task: false,
        task_label: "",
        task_description: "",
        task_start_time: "",
        task_end_time: "",
        task_category: "",
        task_is_group: false
        // End data for tasks
    };    
    
    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {Vue.set(e, '_idx', k++);});
        return a;
    };

    app.set_adding_task = () => {
        app.vue.is_adding_task = true;
    };

    app.add_task = () => {
        axios.post(add_task_url,
            {
                label: app.vue.task_label,
                description: app.vue.task_description,
                categorization: app.vue.task_category,
                is_group: app.vue.task_is_group
            }).then(function (response) {
                app.vue.tasks.push({
                    id: response.data.id,
                    label: app.vue.task_label,
                    description: app.vue.task_description,
                    categorization: app.vue.task_category,
                    is_group: app.vue.task_is_group,
                    created_by: response.data.created_by
                    //no start or end time yet
                    //will implement groups soon
                })
                app.enumerate(app.vue.tasks)
                app.vue.is_adding_task = false;
            })
    }; 

    // This contains all the methods.
    app.methods = {
        set_adding_task: app.set_adding_task,
        add_task: app.add_task
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        app.vue.is_adding_task = false
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code in it. 
init(app);
