document.addEventListener("DOMContentLoaded", () => {

    const form = document.querySelector('.form-panel')
    const select = document.getElementById('option_id')
    const table_body = document.querySelector('.table tbody')

    //Retrieving devices info stored in the local storage
    const stored_devices = JSON.parse(localStorage.getItem('devices'));
    if (!stored_devices){
        console.log('No device info found')
        return;
    }

    //Looping through device info stored in the database
    Object.keys(stored_devices).forEach((device_key)=>{

        const device = stored_devices[device_key]
        const option = document.createElement('option')
        option.value = device_key 
    
        //Assinging the device number and IP automatically
        option.textContent = `${device_key} ${device.ip}`
        select.appendChild(option)

    })

    if (form){
        form.addEventListener('submit', async (e) => {
            e.preventDefault()
            
            const selected_option = select.value.trim()

            if(!selected_option){
                alert("Please select an option")
                return;
            }

            const selected_dev = stored_devices[selected_option]    

            //Sending data via json to api endpoint for processing
            try{
                const response = await fetch('/api/cisco_hardening', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        device_key: selected_option,
                        selected_dev: selected_dev
                    })
                });

                const result = await response.json();

                if(response.ok){
                    console.log('Result:', result);
                    alert(result.results[0].message)

                    const missing_ad_count = result.results[0].missing_ad_count
                    const missing_advice = result.results[0].missing_advice

                    const hard_list = document.getElementById("hard_list")
                    const mis_config = document.getElementById("mis_config")
                    const field = document.querySelector('.field.mis_config')
                    
                    if (missing_ad_count !== 0){
                        hard_list.style.display = 'none'
                        mis_config.style.display = 'flex'

                        //Populating automatically the missing configurations
                        missing_advice.forEach((item) => {
                            const miss_text = document.createElement('p')
                            miss_text.textContent = `${item.commands}`

                            field.appendChild(miss_text)
                    
                        }) 

                        //Fixing the missing configurations 
                        document.getElementById('mis_config_btn').addEventListener('click', async (e) => {
                            e.preventDefault()
                            console.log('Fix configs button clicked...')

                            try{
                                const fix_response = await fetch('api/fix_hardening', {
                                    method: 'POST',
                                    headers: {'Content-Type': 'application/json'},
                                    body: JSON.stringify({
                                        device_key: selected_option,
                                        selected_dev: selected_dev,
                                        missing_advice: missing_advice  

                                    })
                                })

                                const fix_result = await fix_response.json()

                                if (fix_response.ok){
                                    hard_list.style.display = 'flex'
                                    mis_config.style.display = 'none'
                                    
                                    alert(fix_result.results[0].message)
                                    console.log('Result:', fix_result)
                                }

                                else{
                                console.log("Could not fix configurations")
                                }

                                //Display the result in the table
                                table_body.innerHTML = ''; 

                                fix_result.results.forEach((device, index) => {
                                    const row = document.createElement('tr');
                                    row.innerHTML = `
                                        <td>${index + 1}</td>
                                        <td>${device.device}</td>
                                        <td>${device.message.trim()}</td>
                                    
                                    `;
                                    table_body.appendChild(row);
                                });
                            }
                        
                            catch(error){
                                console.log('Error', error);
                            }

                        })
                        
                    }
                    
                    else{
                        alert("No missing configuration to fix")
                    }
                    
                }
            }
            catch (error) {
                console.log('Error', error);
            }
        })
    }
})