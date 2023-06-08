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
        reflection_blocks: [],
        week1: [],
        week2: [],
        week3: [],
        week4: [],
        week5: [],
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
                app.data.reflection_blocks = response.data.reflections;
                app.data.week1 = app.data.reflection_blocks.slice(0, 7);
                app.data.week2 = app.data.reflection_blocks.slice(7, 14);
                app.data.week3 = app.data.reflection_blocks.slice(14, 21);
                app.data.week4 = app.data.reflection_blocks.slice(21, 28);
                app.data.week5 = app.data.reflection_blocks.slice(28, 31);
            });
        // TODO
    };

    // app.generate_blocks = () => {
    //     app.data.reflection_blocks;
    // };

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
        app.data.reflection_blocks = [];
        app.get_reflections();
    };

    app.init();
};

init(app);
