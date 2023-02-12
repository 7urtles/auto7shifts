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
        onStepChanging: function(event, currentIndex)
        {   
            if (currentIndex == 1){
                login = test_submit().then(data => {
                    console.log(data)
                })
                return false;
            }
            return true;
        },
        onFinished: function (event, currentIndex)
        {    
            test_submit()
            // $('#signup-form').attr('action', '/submit')
            // document.getElementById("submit-button").click();
        }
    });
})(jQuery);

test_submit = async() => {
    const days = document.querySelectorAll('[category="days"] :checked')
    const roles = document.querySelectorAll('[category="roles"] :checked')
    const locations = document.querySelectorAll('[category="locations"] :checked')
    // const contact = document.querySelectorAll('[category="contact"]')
    const login = document.querySelectorAll('[category="login"]')
    
    form_data = {
        requested:{
            days: [...days].map(option => option.value),
            roles: [...roles].map(option => option.value),
            locations: [...locations].map(option => option.value),
            
        },
        account:{
            // contact: [...contact].map(option => option.value),
            login: [...login].map(option => option.value),
        }
    }


    const url = 'http://localhost:5007/submit/jmfjv7456SKaDfh3572f9456faKLFJDS';
    const res = await fetch(url, {
        
        method: 'POST',
        headers: {
            'Content-Type' : 'application/json',
        },
        body: JSON.stringify(form_data),
    });
    return await res
}
