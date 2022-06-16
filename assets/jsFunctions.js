window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        large_params_function: function(site_name) {
            if (site_name == undefined ){
                return site_name;
            }            
            window.open(site_name);
            return site_name;
        }
    }
});