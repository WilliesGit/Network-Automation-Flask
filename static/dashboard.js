document.addEventListener('DOMContentLoaded', () => {
    const device_btn = document.getElementById('device-btn');

    if (device_btn) {
        device_btn.addEventListener('click', () => {
            console.log('Primary button clicked!');
        });

    }
})