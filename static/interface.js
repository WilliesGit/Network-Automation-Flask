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

            //Creating a object to store interface configurations
            const interface_configs = {} 
            
            //Loop through device cards to retrieve hostnames input
            device_cards.forEach((device_card, index) => {
                const device_tag = device_tags[index]
                
                //Accessing interface input for each device and store the value
                const int_input = device_card.querySelector(`#dev${index + 1}_int_num`).value.trim()
                const ip_input = device_card.querySelector(`#dev${index + 1}_int_ip`).value.trim()
                const mask_input = device_card.querySelector(`#dev${index + 1}_int_mask`).value.trim()


                //Calling the checkEmptyInput functions()
                checkEmptyInput(int_input, device_tag, device_card)
                checkEmptyInput(ip_input, device_tag, device_card)
                checkEmptyInput(mask_input, device_tag, device_card)
                
                //To check hostname input is not empty
                if(!int_input && !ip_input && !mask_input){
                    is_valid = false;
                }
                    
            })
            
            if(!is_valid){
                console.log("Device cards are required")
                return;
            }
            
            else {
              
                Object.keys(stored_devices).forEach((device_key) =>{
                    //Appending interface configuration input
                    interface_configs[device_key] = {
                        interface : document.getElementById(`${device_key}_int_num`).value.trim(),
                        ip: document.getElementById(`${device_key}_int_ip`).value.trim(),
                        mask: document.getElementById(`${device_key}_int_mask`).value.trim(),
                    }
                    
                })
            }
              
            console.log("Sumbitting form...")
          
            //Sending data via json to api endpoint for processing
            try{
                const response = await fetch('/api/interface_config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        devices: stored_devices,
                        interface_configs: interface_configs
                     })
                });

                const result = await response.json();
               
                if(response.ok){
                    console.log('Result:', result);
                    alert("Configuration Completed!")
                    
                }

                //Display the result in the table
                table_body.innerHTML = '';

                result.results.forEach((device, index) => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${index + 1}</td>
                        <td>${device.device}</td>
                        <td>${device.interface_info.trim()}</td>
                    
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