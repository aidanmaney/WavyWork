// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
       
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

    // This contains all the methods.
    app.methods = {

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
        axios.get(get_users_url, {params: {query: ""}}).then(function (response){
            app.vue.following = app.enumerate(response.data.following)
            app.vue.non_following = app.enumerate(response.data.non_following)
        })
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code in it. 
init(app);
