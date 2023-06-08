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
    received_urls: [],
  };

  app.enumerate = (a) => {
    // This adds an _idx field to each element of the array.
    let k = 0;
    a.map((e) => {
      e._idx = k++;
    });
    return a;
  };
  // Get all users for the share page
  app.get_all_users = () => {
    axios
      .get(get_users_url, { params: { url_id: url_id } })
      .then(function (response) {
        const newUsers = response.data.rows.map((user) => {
          return {
            username: user.username,
            last_name: user.last_name,
            first_name: user.first_name,
            id: user.id,
            is_shared: user.is_shared,
          };
        });

        // Filter out users that already exist in app.vue.users
        const filteredUsers = newUsers.filter((user) => {
          return !app.vue.users.some(
            (existingUser) => existingUser.id === user.id
          );
        });

        console.log(newUsers);
        // Append the filtered users to app.vue.users
        app.vue.users = app.vue.users.concat(filteredUsers);
      })
      .catch(function (error) {
        console.log(error);
      });
  };
  // search user by username
  app.search = () => {
    if (app.vue.search_text === "") {
      app.vue.users = [];
      app.get_all_users();
      return;
    }
    axios
      .get(get_users_url, {
        params: { q: app.vue.search_text, url_id: url_id },
      })
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

  // Send (share) url to user
  app.send = (user_id) => {
    axios
      .post(send_url, { url_id: url_id, shared_with: user_id })
      .then((response) => {
        console.log(response.data);
        app.get_all_users();
        window.location.reload();
      })
      .catch((error) => {
        console.error(error);
      });
  };

  // Get all received urls
  app.get_received_urls = () => {
    axios
      .get(get_received_url)
      .then((response) => {
        console.log(response.data);
        const received_urls = response.data.rows.map((url) => {
          return {
            id: url.id,
            url_name: url.url_name,
            long_url: url.long_url,
            short_url: "localhost:8000/shortener/redirect/" + url.short_id,
            created_at: url.created_at,
            shared_by: {
              id: url.shared_by.id,
              username: url.shared_by.username,
              first_name: url.shared_by.first_name,
              last_name: url.shared_by.last_name,
            },
          };
        });
        app.vue.received_urls = received_urls;
      })
      .catch((error) => {
        console.error(error);
      });
  };
  // Copy short url to clipboard
  app.copyToClipboard = (url) => {
    navigator.clipboard.writeText(url);
  };

  // Reshare url
  app.reshare = (url_id) => {
    window.location.pathname = "/shortener/share/" + url_id + "/";
  };

  // This contains all the methods.
  app.methods = {
    // Complete as you see fit.
    get_all_users: app.get_all_users,
    send: app.send,
    search: app.search,
    get_received_urls: app.get_received_urls,
    copyToClipboard: app.copyToClipboard,
    reshare: app.reshare,
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
    // share or received?
    switch (page) {
      case "share":
        app.get_all_users();
        break;
      case "received":
        app.get_received_urls();
    }
  };

  // Call to the initializer.
  app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code in it.
init(app);
