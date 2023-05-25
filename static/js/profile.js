// This will be the object that will contain the Vue attributes
// and be used to initialize it.
const app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
const init = (app) => {
  app.data = {
    days_of_the_week: [
      'Mon',
      'Tue',
      'Wed',
      'Thu',
      'Fri',
      'Sat',
      'Sun',
    ],
  };

  app.enumerate = (a) => {
    let k = 0;
    a?.map((e) => {
      e._idx = k++;
    });
    return a;
  };

  app.methods = {};

  app.vue = new Vue({
    el: '#vue-target',
    data: function() {
      return app.data;
    },
    methods: app.methods,
  });

  app.init = () => {};

  app.init();
};

init(app);
