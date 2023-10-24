function disableButton(event) {
    event.target.value = "Loading...";
    // Delay disabling the button until after the form submission
    setTimeout(function() {
        event.target.disabled = true;
    }, 10);
}