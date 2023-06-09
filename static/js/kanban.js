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
        app.vue.current_board = board
        app.get_tasks()
    }

    // get tasks (board)
    // should return five arrays (todo, in_progress, etc) with the task in each array
    app.get_tasks = function (){
        axios.get(get_tasks_url, {params: {board: app.vue.current_board}}).then(function (response) { // {params: {board: app.vue.current_board}}
            app.vue.task_arrays["todo"] = app.enumerate(response.data.todo_tasks)
            app.vue.task_arrays["in_progress"] = app.enumerate(response.data.in_progress_tasks)
            app.vue.task_arrays["stuck"] = app.enumerate(response.data.stuck_tasks)
            app.vue.task_arrays["done"] = app.enumerate(response.data.done_tasks)
            
            for (array_key in app.vue.task_arrays){
                array = app.vue.task_arrays[array_key]
                for (obj_key in array){
                    obj = array[obj_key]
                    
                    const start_event = new Date(obj.tasks.start_time.substring(0, 4), obj.tasks.start_time.substring(5, 7), obj.tasks.start_time.substring(9, 11))
                    const end_event = new Date(obj.tasks.end_time.substring(0, 4), obj.tasks.end_time.substring(5, 7), obj.tasks.end_time.substring(9, 11))
                    
                    obj.tasks.start_time = start_event.toDateString()
                    obj.tasks.end_time = end_event.toDateString()   
                }   
            }
        })
    }

    app.move_task_1 = function (obj_idx, column) {
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

        axios.post(update_kanban_url, {task_id: task.kanban_cards.task_id, new_column: post_column}).then(function(response) {
            app.vue.task_arrays[post_column].unshift(task)
            
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
        app.get_tasks()
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code in it. 
init(app);
