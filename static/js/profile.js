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
        week6: [],
        month: "",

        journal_entry: "",
    };

    app.enumerate = (a) => {
        let k = 0;
        a?.map((e) => {
            e._idx = k++;
        });
        return a;
    };

    app.get_reflections = () => {
        axios
            .get(get_reflections_url, {
                params: { pmo: app.data.prevMonthOffset },
            })
            .then(function (response) {
                app.data.reflection_blocks = response.data.reflections;

                for (var i = 0; i < response.data.start_of_month_offset; i++) {
                    app.data.reflection_blocks.unshift({
                        day: null,
                        prod_lvl: null,
                    });
                }

                console.log(app.data.reflection_blocks);

                n_padding_blocks = 42 - app.data.reflection_blocks.length;
                for (var i = 0; i < n_padding_blocks; i++) {
                    app.data.reflection_blocks.push({
                        day: null,
                        prod_lvl: null,
                    });
                }

                app.data.week1 = app.data.reflection_blocks.slice(0, 7);
                app.data.week2 = app.data.reflection_blocks.slice(7, 14);
                app.data.week3 = app.data.reflection_blocks.slice(14, 21);
                app.data.week4 = app.data.reflection_blocks.slice(21, 28);
                app.data.week5 = app.data.reflection_blocks.slice(28, 35);
                app.data.week6 = app.data.reflection_blocks.slice(35);

                app.data.month = response.data.month;
            });
    };

    app.goBackMonth = () => {
        app.data.prevMonthOffset += 1;
        app.get_reflections();
    };

    app.goForwardMonth = () => {
        if (app.data.prevMonthOffset >= 1) {
            app.data.prevMonthOffset -= 1;
            app.get_reflections();
        }
    };

    app.open_journal_modal = (day) => {
        axios.post(get_journal_entry_by_day_url, {day:day}).then( (res) => {
            app.vue.journal_entry = res.data.entry
            document.getElementById("calendar_journal_modal").classList.add("is-active");
        })
    }

    app.methods = {
        goForwardMonth: app.goForwardMonth,
        goBackMonth: app.goBackMonth,
        get_reflections: app.get_reflections,
        open_journal_modal: app.open_journal_modal
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
        app.data.month = "";
        app.data.reflection_blocks = [];
        app.get_reflections();
    };

    app.init();
};

init(app);
