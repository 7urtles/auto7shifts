(function($) {
    var form = $("#signup-form");
    form.steps({
        headerTag: "h3",
        bodyTag: "fieldset",
        transitionEffect: "fade",
        labels: {
            previous : 'Previous',
            next : 'Next',
            finish : 'Submit',
            current : ''
        },
        titleTemplate : '<div class="title"><span class="title-text">#title#</span><span class="title-number">0#index#</span></div>',
        onFinished: function (event, currentIndex)
        {    
            test_submit()   
            // $('#signup-form').attr('action', '/submit')
            // document.getElementById("submit-button").click();
        }
    });
})(jQuery);

async function test_submit(){
    var days = document.querySelectorAll('[category="days"] :checked')
    var roles = document.querySelectorAll('[category="roles"] :checked')
    var locations = document.querySelectorAll('[category="locations"] :checked')
    var contact = document.querySelectorAll('[category="contact"]')
    var login = document.querySelectorAll('[category="login"]')
    
    form_data = {
        requested:{
            days: [...days].map(option => option.value),
            roles: [...roles].map(option => option.value),
            locations: [...locations].map(option => option.value),
            
        },
        account:{
            contact: [...contact].map(option => option.value),
            login: [...login].map(option => option.value),
        }
    }


    let url = 'http://localhost:5007/submit';
    let data = form_data;

    let res = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });
}
