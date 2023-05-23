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
        task_category: ""
        // End data for tasks
    };    
    
    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {Vue.set(e, '_idx', k++);});
        return a;
    };

    app.add_task = () => {

    };

    // This contains all the methods.
    app.methods = {
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

    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code in it. 
init(app);
