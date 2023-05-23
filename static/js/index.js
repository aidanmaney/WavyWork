// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
       day: new Date(this.value).getDate(),
       month: new Date(this.value).getMonth(),
       year: new Date(this.value).getFullYear(),
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

    app.store_date = function() {
        // const timestamp = Date.parse(`${app.vue.year.padStart(4, 0)}-${app.vue.month}-${app.vue.day}`);
        // if (Number.isNaN(timestamp)) return;
        if (isNaN(app.vue.year) || isNaN(app.vue.day) || isNaN(app.vue.month)) {
            return;
        } else {
        console.log("DATE", app.vue.day, app.vue.month, app.vue.year)
        }
    }

    // This contains all the methods.
    app.methods = {
        store_date: app.store_date,
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
        
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code in it. 
init(app);
