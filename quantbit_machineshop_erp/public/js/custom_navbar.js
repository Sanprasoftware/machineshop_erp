$(document).ready(async function () {
    const $navbar = $('.navbar');

    if ($navbar.length) {
        let response = await frappe.call({
            method: "frappe.core.doctype.session_default_settings.session_default_settings.get_session_default_values"
        })
        let company_headline = (await frappe.db.get_value("Company", JSON.parse(response.message)[0].default, "custom_company__headline")).message.custom_company__headline;
        const companyDiv = (`<div class="navbar-hello">${company_headline || JSON.parse(response.message)[0].default}</div>`);
        function cookieToObject(cookieString) {
            const cookies = cookieString.split(';');
            const cookieObject = {};

            cookies.forEach(cookie => {
                const [key, value] = cookie.trim().split('=');
                cookieObject[key] = value;
            });

            return cookieObject;
        }
        let data = cookieToObject(document.cookie);
        let theme = (await frappe.db.get_value("User", decodeURIComponent(data.user_id), "desk_theme")).message;
        if (theme.desk_theme == "Light"){
            frappe.dom.set_style(`
                .navbar {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
    
                .navbar-hello {
                    display: inline-block;
                    padding: 5px 10px;
                    border-radius: 4px;
                    font-weight: 700;
                    color:rgb(29, 29, 30);
                    position: absolute;
                    left: 50%;
                    transform: translateX(-50%);
                }
            `);
        }else{
            frappe.dom.set_style(`
                .navbar {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
    
                .navbar-hello {
                    display: inline-block;
                    padding: 5px 10px;
                    border-radius: 4px;
                    font-weight: 700;
                    color:rgb(255, 255, 255);
                    position: absolute;
                    left: 50%;
                    transform: translateX(-50%);
                }
            `);
        }
       

        // console.log(JSON.parse(response.message)[0].default)
        $navbar.append(companyDiv);
    }
});
