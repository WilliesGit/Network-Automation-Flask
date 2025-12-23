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
            console.log("Sumbitting form...")

            const selected_option = select.value.trim()

            if(!selected_option){
                alert("Please select an option")
                return;
            }

            const selected_dev = stored_devices[selected_option]

            //Sending data via json to api endpoint for processing
            try{
                const response = await fetch('/api/compare_configs', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json' },
                    body: JSON.stringify({device_key: selected_option})
                });

                const result = await response.json();

                if(response.ok){
                    console.log('Result:', result);
                    alert(result.results[0].message)
                    
                }

                //Display the result in the table
                table_body.innerHTML = ''; // Clear the table body

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