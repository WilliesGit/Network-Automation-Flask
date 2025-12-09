document.addEventListener("DOMContentLoaded", () => {

    const form = document.querySelector('.form-panel')
    const table_body = document.querySelector('.table tbody')

    //Retrieving devices info stored in the local storage
    const stored_devices = JSON.parse(localStorage.getItem('devices'));
    if (!stored_devices){
        console.log('No device info found')
        return;
    }

    
    if (form && table_body){
        form.addEventListener('submit', async (e) => {
            e.preventDefault()
            console.log("Hostnames entered")

            //Function to check for empty fields
            function checkEmptyInput(input_value, device_tag, device_card){
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
            
            //Creating a object to store hostnames info
            const hostnames = {} 
            
            //Loop through device cards to retrieve hostnames input
            device_cards.forEach((device_card, index) => {
                const device_tag = device_tags[index]
                const device_key = `dev${index + 1}`

                if (stored_devices[device_key]){
                    //variable to store each device info
                    const device = stored_devices[device_key] 
                    
                    //Accessing hostname for each device and store the value
                    const hostname_input = device_card.querySelector(`#dev${index + 1}_host`).value.trim()

                    //Calling the checkEmptyInput() functions
                    checkEmptyInput(hostname_input, device_tag, device_card)
                    
                    //To check hostname input is not empty
                    if(!hostname_input){
                        is_valid = false;
                    }
                    
                    else {
                        //Appending hostname to existing device data
                        hostnames[device_key] = {
                            hostname : hostname_input
                        }
                    }
                }
            })
            
            if(!is_valid){
                console.log("Device cards are required")
                return;
            }
            
            console.log("Sumbitting form...")

            //Sending data via json to api endpoint for processing
            try{
                const response = await fetch('/api/hostname_config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ devices: hostnames })
                });
                const result = await response.json();
                
                if(response.ok){
                    console.log('Result:', result);
                    alert("Hostnames configured!")
                    
                }

                //Display the result in the table
                table_body.innerHTML = ''; // Clear the table body

                result.devices.forEach((device, index) => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${index + 1}</td>
                        <td>${device.ip}</td>
                        <td>${device.username}</td>
                        <td>${device.hostname}</td>
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