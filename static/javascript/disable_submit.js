document.addEventListener('DOMContentLoaded', function(){
    var form = document.querySelector('form');
    var button = document.querySelector('#submit-btn');

    form.addEventListener('submit', function(){
        button.setAttribute('disabled', 'disabled');
    });
});