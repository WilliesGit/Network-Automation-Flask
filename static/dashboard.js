document.addEventListener("DOMContentLoaded", () => {

    const form = document.querySelector('.form-panel')

    if (form){
        form.addEventListener('submit', async (e) => {
            e.preventDefault()
            console.log("Configuration submitted")

            //Function to check for empty fields
            function checkEmptyInput(input_value, device_tag, device_card, skip_secret){

                if(skip_secret && input_value === ""){
                    return;
                }

                if (!input_value){
                     device_tag.textContent = '**Required'
                     device_card.style.borderColor = 'red';
                }

                else{
                    device_tag.textContent = ''
                    device_card.style.borderColor = ''
                }
            }


            const device_tags = document.querySelectorAll('.device-tag')
            const device_cards = document.querySelectorAll('.device-card.primary')
            let is_valid = true;

            //Creating a object to store device info
            const devices = {} 

            device_cards.forEach((device_card, index) => {

                const device_tag = device_tags[index]

                const ip_input = device_card.querySelector(`#dev${index + 1}_ip`).value.trim()
                const user_input = device_card.querySelector(`#dev${index + 1}_user`).value.trim()
                const pass_input = device_card.querySelector(`#dev${index + 1}_pass`).value.trim()
                const secret_input = device_card.querySelector(`#dev${index + 1}_secret`).value.trim()
                

                //Calling the checkEmptyInput() function
                checkEmptyInput(ip_input, device_tag, device_card, false)
                checkEmptyInput(user_input, device_tag, device_card, false)
                checkEmptyInput(pass_input, device_tag, device_card, false)
                checkEmptyInput(secret_input, device_tag, device_card, true)
               
                if(!ip_input && !user_input && !pass_input){
                    is_valid = false;
                }

            })

            if(!is_valid){
                console.log("Device cards are required")
                return;
            }

            else{
                console.log("Sumbitting form...")

                //Function to get device info
                function deviceInfo(device_id){
                    return {
                        ip: document.getElementById(`${device_id}_ip`).value.trim(),
                        username: document.getElementById(`${device_id}_user`).value.trim(),
                        password: document.getElementById(`${device_id}_pass`).value.trim(),
                        secret: document.getElementById(`${device_id}_secret`).value.trim()
                    }
                }
                    //Storing device info in devices object
                    devices.dev1 = deviceInfo('dev1'),
                    devices.dev2 = deviceInfo('dev2'),
                    devices.dev3 = deviceInfo('dev3')

            }

            //Creating a secure data object without password and secret
            const secure_data = {}

            //Stores data without password and secret
            Object.keys(devices).forEach((device_key) =>{
                const dev = devices[device_key]
                secure_data[device_key] = {
                    ip: dev.ip,
                    username: dev.username
                }
            })
            
            //Store the secured data for devices object in localStorage
            localStorage.setItem('devices', JSON.stringify(secure_data));

            //Sending data via json to api endpoint for processing
            try{
                const response = await fetch('/api/device_info', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                       devices:  devices
                    })
                })

                const result = await response.json()

                if(response.ok){
                    console.log('Result:', result);
                    alert("Devices info stored successfully")
                    
                }
               
            }

            catch(error){
                console.log('Error', error)
                alert(error)
            }

            
        })
    }
})