// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
       
       task_arrays: {
        "todo": [],
        "in_progress": [],
        "stuck": [],
        "done": []
       },
    //    backlog_tasks: [],
       current_board: "personal",
       show_new_column: false,
       moving_task_id: 0,
       moving_task_pre_column: "",
    };    
    
    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        if (a.length === 0) {
            return a;
        }
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };    

    app.set_board = function(board) {
        console.log("here here")

        app.vue.current_board = board
        app.get_tasks()
    }

    // get tasks (board)
    // should return five arrays (todo, in_progress, etc) with the task in each array
    app.get_tasks = function (){
        // console.log("ENTERED")
        axios.get(get_tasks_url, {params: {board: app.vue.current_board}}).then(function (response) { // {params: {board: app.vue.current_board}}
            app.vue.task_arrays["todo"] = app.enumerate(response.data.todo_tasks)
            app.vue.task_arrays["in_progress"] = app.enumerate(response.data.in_progress_tasks)
            app.vue.task_arrays["stuck"] = app.enumerate(response.data.stuck_tasks)
            app.vue.task_arrays["done"] = app.enumerate(response.data.done_tasks)
            console.log("SAVED VALUES")
            // app.vue.backlog_tasks = app.enumerate(response.data.backlog_tasks)
        })
    }

    app.move_task_1 = function (obj_idx, column) {
        console.log("CLICKED", obj_idx, column)
        if (app.vue.show_new_column) {
            app.vue.show_new_column = false
            app.vue.moving_task_id = 0
            app.vue.moving_task_pre_column = ""
        } else {
            app.vue.show_new_column = true
            app.vue.moving_task_id = obj_idx
            app.vue.moving_task_pre_column = column
        }
        
    }

    app.move_task_2 = function(post_column) {
        task = app.vue.task_arrays[app.vue.moving_task_pre_column][app.vue.moving_task_id]
        task.kanban_cards.column = post_column

        console.log("MOVE TASK 2")

        axios.post(update_kanban_url, {task_id: task.kanban_cards.task_id, new_column: post_column}).then(function(response) {
            // SEND KANBAN ID 
       
            // add to post column
            app.vue.task_arrays[post_column].unshift(task)
            // // removing from pre column
            app.vue.task_arrays[app.vue.moving_task_pre_column].splice(app.vue.moving_task_id, 1)

            app.vue.task_arrays[post_column] = app.enumerate(app.vue.task_arrays[post_column])
            app.vue.task_arrays[app.vue.moving_task_pre_column] = app.enumerate(app.vue.task_arrays[app.vue.moving_task_pre_column])

            app.vue.show_new_column = false
            app.vue.moving_task_id = 0
            app.vue.moving_task_pre_column = ""
        })

        
    }

    // This contains all the methods.
    app.methods = {
        get_tasks: app.get_tasks,
        move_task_1: app.move_task_1,
        move_task_2: app.move_task_2,
        set_board: app.set_board,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // get all the users for an empty query and set it to results
        // axios.get(get_tasks_url)
        app.get_tasks()

        console.log("HELLO HI")
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code in it. 
init(app);
