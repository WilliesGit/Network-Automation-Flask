document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('.form-panel')
    const select = document.getElementById('route_id')
    const table_body = document.querySelector('.table tbody')
    
    //Retrieving devices info stored in the local storage
    const stored_devices = JSON.parse(localStorage.getItem('devices'));
    if (!stored_devices){
        console.log('No device info found')
        return;
    }

    //Routing Protocol sections
    const ospf_card = document.getElementById('ospf-card')
    const eigrp_card = document.getElementById('eigrp-card')
    const rip_card = document.getElementById('rip-card')

    //Function to show/hide Routing Protocol sections based on selection
    function protocolSelect(selected_option) {
    
        ospf_card.style.display = 'none'
        eigrp_card.style.display = 'none'
        rip_card.style.display = 'none'
               
        if(selected_option === 'OSPF'){
             ospf_card.style.display = 'block'
        }
        else if (selected_option == 'RIP'){
             rip_card.style.display = 'block'
        }
        else if(selected_option == 'EIGRP') {
            eigrp_card.style.display = 'block'
        }
    
    }

    //Event listener for Routing Protocol selection
    select.addEventListener('change', (e) => {
        const value = e.target.value.trim()
        protocolSelect(value)
    })

    protocolSelect(select.value.trim())


    if (form){
        form.addEventListener('submit', async (e) => {
            e.preventDefault()
            console.log("Sumbitting form...")
            

            const selected_option = select.value.trim()

            if(!selected_option){
                alert("Please select a routing protocol")
                return;
            }

            //OSPF inputs
            const id_input = document.getElementById('ospf_process').value.trim()
            const area_input = document.getElementById('ospf_area').value.trim()
            const ospf_ip_input = document.getElementById('ospf_network_ip').value.trim()
            const ospf_mask_input = document.getElementById('ospf_network_mask').value.trim()

            //EIGRP inputs
            const as_input = document.getElementById('eigrp_as').value.trim()
            const eigrp_ip_input = document.getElementById('eigrp_network_ip').value.trim()
            const eigrp_mask_input = document.getElementById('eigrp_network_mask').value.trim()

            //RIP input
            const rip_input = document.getElementById('rip_network_ip').value.trim()
            

            //OSPF Validation
            if(selected_option === "OSPF"){

                if(!id_input || !area_input || !ospf_ip_input || !ospf_mask_input){
                    alert("All fields are required")
                    return;

                }
            }

            //EIGRP Validation
            else if(selected_option === "EIGRP"){
                if (!as_input || !eigrp_ip_input || !eigrp_mask_input){
                    alert("All fields are required")
                    return;
                }

            }

            //RIP Validation
            else if(selected_option === "RIP"){
                if (!rip_input){
                    alert("All fields are required")
                    return;
                }
    

            }
           
            //Creating a object to store routing protocol configurations
            const route_config = {}
           
            //Appending routing protocol configuration input
            Object.keys(stored_devices).forEach((device_key) =>{
                if(selected_option === "OSPF"){
                    route_config[device_key] = {
                        protocol : "OSPF",
                        process_id : document.getElementById('ospf_process').value.trim(),
                        area :  document.getElementById('ospf_area').value.trim(),
                        ip: document.getElementById('ospf_network_ip').value.trim(),
                        mask: document.getElementById('ospf_network_mask').value.trim()
                    }     
                }

                else if(selected_option == "EIGRP"){
                    route_config[device_key] = {
                        protocol : "EIGRP",
                        as_num : document.getElementById('eigrp_as').value.trim(),
                        ip: document.getElementById('eigrp_network_ip').value.trim(),
                        mask: document.getElementById('eigrp_network_mask').value.trim()
                    }
                }

                else if(selected_option == "RIP"){
                    route_config[device_key] = {
                        protocol : "RIP",
                        ip: document.getElementById('rip_network_ip').value.trim(),

                    }
                }

            })

            //Sending data via json to api endpoint for processing
            try{
                const response = await fetch('/api/route_protocol', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        devices : stored_devices,
                        route_protocol: selected_option,
                        route_config: route_config
                    })
                });

                const result = await response.json();

                if(response.ok){
                    console.log('Result:', result);
                    alert(result.results[0].message)
                    
                }

                //Display the result in the table
                table_body.innerHTML = '';

                result.results.forEach((device, index) => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${index + 1}</td>
                        <td>${device.device}</td>
                        <td>${device.route_info.trim()}</td>
                    
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