document.addEventListener('DOMContentLoaded', function(){
    var forms = document.querySelectorAll('form');

    forms.forEach(function(form) {
        var button = form.querySelector('.btn');

        form.addEventListener('submit', function(event){
            button.value = "Loading...";
            setTimeout(function() {
                button.setAttribute('disabled', 'disabled');
            }, 10);
        });
    });
});