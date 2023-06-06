// This will be the object that will contain the Vue attributes
// and be used to initialize it.
const app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
const init = (app) => {
    app.data = {
        daysOfTheWeek: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        // How many months *back* is the user looking
        prevMonthOffset: 0,
        reflections_day_level: [],
    };

    app.enumerate = (a) => {
        let k = 0;
        a?.map((e) => {
            e._idx = k++;
        });
        return a;
    };

    // app.goForwardMonth = () => {
    //   if (app.vue.data.prevMonthOffset >= 1) {
    //     app.vue.data.prevMonthOffset -= 1;
    //   }
    // };

    app.get_reflections = () => {
        axios
            .get(get_reflections_url, {
                params: { pmo: app.data.prevMonthOffset },
            })
            .then(function (response) {
                app.data.reflections_day_level = response.data.reflections;
                // TODO
            });
    };

    app.methods = {
        // goForwardMonth: app.goForwardMonth,
        // goBackMonth: app.goBackMonth,
        get_reflections: app.get_reflections,
    };

    app.vue = new Vue({
        el: "#vue-target",
        data: function () {
            return app.data;
        },
        methods: app.methods,
    });

    app.init = () => {
        app.data.prevMonthOffset = 0;
        app.data.reflections_day_level = [];
    };

    app.init();
};

init(app);
