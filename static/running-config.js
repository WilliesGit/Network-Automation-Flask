document.addEventListener("DOMContentLoaded", () => {

    const form = document.querySelector('.form-panel')
    const device_cards = document.querySelectorAll('.device-card.primary')
    const device_tags = document.querySelectorAll('.device-tag')
    const table_body = document.querySelector('.table tbody')

    //Retrieving devices info stored in the local storage
    const stored_devices = JSON.parse(localStorage.getItem('devices'));
    if (!stored_devices){
        console.log('No device info found')
        return;
    }

    device_cards.forEach((device_card, index) => {
        const device_key = `dev${index + 1}`

        if (stored_devices[device_key]){
            //Retrieving the data for the each device
            const device = stored_devices[device_key] 

            //Function to pre-populate input field with device info from database
            const fillInputField = (field_name, value) => {
                const input_field = document.getElementById(`dev${index + 1}_${field_name}`)

                if (input_field && value){
                    input_field.value = value
                }
            }

            //Calling the fillInputField function for each input field
            fillInputField('ip', device.ip)
            fillInputField('user', device.username)
            fillInputField('pass', device.password)  
            fillInputField('secret', device.secret)        
        } 

        
    })


    if (form){
        form.addEventListener('submit', async (e) => {
            e.preventDefault()
           
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

            //Creating a object to store device info
            const devices = {}
            let is_valid = true;

            device_cards.forEach((device_card, index) =>{
                const device_tag = device_tags[index]

                const ip_input = device_card.querySelector(`#dev${index + 1}_ip`).value.trim()
                const user_input = device_card.querySelector(`#dev${index + 1}_user`).value.trim()
                const pass_input = device_card.querySelector(`#dev${index + 1}_pass`).value.trim()
                const secret_input = device_card.querySelector(`#dev${index + 1}_secret`).value.trim()
                

                //Calling the check input functions
                checkEmptyInput(ip_input, device_tag, device_card, false)
                checkEmptyInput(user_input, device_tag, device_card, false)
                checkEmptyInput(pass_input, device_tag, device_card, false)
                checkEmptyInput(secret_input, device_tag, device_card, true)
               
                if(!ip_input || !user_input || !pass_input){
                    is_valid = false;
                    return false;
                }

                return false;
            })

            if(!is_valid){
                alert("All fields are required")
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
                    //Storing device info in the devices object
                    devices.dev1 = deviceInfo('dev1'),
                    devices.dev2 = deviceInfo('dev2'),
                    devices.dev3 = deviceInfo('dev3')
            }

            //Sending data via json to api endpoint for processing
            try{
                const response = await fetch('/api/running_config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ devices: devices})
                });
                const result = await response.json();
                

                if(response.ok){
                    console.log('Result:', result);
                    alert("Running configuration saved to file")
                    
                }

                //Display the result in the table
                table_body.innerHTML = ''; 
                result.results.forEach((device, index) => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${index + 1}</td>
                        <td>${device.device}</td>
                        <td>${device.message.trim()}</td>
                    
                    `;
                    table_body.appendChild(row);
                });

            }
            catch (error) {
                console.log('Error', error);
            }
        })
    }
})