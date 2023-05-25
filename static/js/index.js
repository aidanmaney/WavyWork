// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete as you see fit.
        // content: [],
    };    
    
    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };    


    // app.follow = funct () {
    //  axios.post(set_follow_url).then(function(response)) {
        // console.log(response)
        // app.data.query =

    // }


 

    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        // get_users: app.get_users,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        console.log("Top of init()")
        // app.search()
        // app.get_users()
        
        // Put here any initialization code.
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code in it. 
console.log('Top level')
init(app);