// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {
  // This is the Vue data.
  app.data = {
    // Complete as you see fit.
    search_text: "",
    users: [],
  };

  app.enumerate = (a) => {
    // This adds an _idx field to each element of the array.
    let k = 0;
    a.map((e) => {
      e._idx = k++;
    });
    return a;
  };

  app.get_all_users = () => {
    axios
      .get(get_users_url)
      .then(function (response) {
        const users = response.data.rows.map((user) => {
          return {
            username: user.username,
            last_name: user.last_name,
            first_name: user.first_name,
            id: user.id,
            isShared: false,
          };
        });
        app.vue.users = users;
      })
      .catch(function (error) {
        console.log(error);
      });
  };

  app.search = () => {
    if (app.vue.search_text === "") {
      app.vue.users = [];
      app.get_all_users();
      return;
    }
    axios
      .get(get_users_url, { params: { q: app.vue.search_text } })
      .then(function (response) {
        const searchResults = response.data.rows.map((user) => {
          return {
            id: user.id,
            username: user.username,
            first_name: user.first_name,
            last_name: user.last_name,
          };
        });
        app.vue.users = searchResults;
      });
  };

  app.send = (user_id) => {
    axios
      .post(send_url, { url_id: url_id, shared_with: user_id })
      .then((response) => {
        console.log(response.data);
      })
      .catch((error) => {
        console.error(error);
      });
  };

  // This contains all the methods.
  app.methods = {
    // Complete as you see fit.
    get_all_users: app.get_all_users,
    send: app.send,
    search: app.search,
  };

  // This creates the Vue instance.
  app.vue = new Vue({
    el: "#vue-target",
    data: app.data,
    methods: app.methods,
  });

  // And this initializes it.
  app.init = () => {
    // Put here any initialization code.
    app.get_all_users();
  };

  // Call to the initializer.
  app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code in it.
init(app);
