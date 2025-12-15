document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('.form-panel')
    const select_acl = document.getElementById('acl_id')
    const select_dir = document.getElementById('dir_id')
    const table_body = document.querySelector('.table tbody')
    

    //Retrieving devices info stored in the local storage
    const stored_devices = JSON.parse(localStorage.getItem('devices'));
    if (!stored_devices){
        console.log('No device info found')
        return;
    }

    //ACL and Direction sections
    const acl_st = document.getElementById('acl_st')
    const ext_acl = document.getElementById('ext_acl')
    const dir_in = document.getElementById('dir_in')
    const dir_out = document.getElementById('dir_out')
    
    //Function to show/hide ACL sections based on selection
    function aclSelect(acl_option) {
    
        acl_st.style.display = 'none'
        ext_acl.style.display = 'none'
               
        if(acl_option === 'Standard'){
             acl_st.style.display = 'block'
        }
        else if (acl_option == 'Extended'){
             ext_acl.style.display = 'block'
        }
    }

      //Function to show/hide Direction sections based on selection
      function dirSelect(dir_option) {
    
        dir_in.style.display = 'none'
        dir_out.style.display = 'none'
        
               
        if(dir_option === 'in'){
             dir_in.style.display = 'block'
        }
        else if (dir_option == 'out'){
             dir_out.style.display = 'block'
        }
    }

    //Event listeners for ACL and Direction selection
    select_acl.addEventListener('change', (e) => {
        const value = e.target.value.trim()
        aclSelect(value)
    })

    aclSelect(select_acl.value.trim())

    select_dir.addEventListener('change', (e) => {
        const value = e.target.value.trim()
        dirSelect(value)
    })

    dirSelect(select_dir.value.trim())

    

    if (form){
        form.addEventListener('submit', async (e) => {
            e.preventDefault()
            console.log("Sumbitting form...")

            //Retrieving selected options
            const selected_acl = select_acl.value.trim()
            const selected_dir = select_dir.value.trim()

            if(!selected_acl || !selected_dir){
                alert("Please select an option")
                return;
            }

            
            //Standard ACL 
            const st_deny_no = document.getElementById('st-deny-no').value.trim();
            const st_deny_action = document.getElementById('st-deny').value.trim();
            const st_deny_source = document.getElementById('st-deny-source').value.trim();
            

            // Extended ACL
            const ex_deny_no = document.getElementById('ex-deny-no').value.trim();
            const ex_deny_action = document.getElementById('ex-deny').value.trim();
            const ex_deny_protocol = document.getElementById('ex-deny-prot').value.trim();
            

            // Direction
            const in_interface = document.getElementById('in_int').value.trim();
            const in_group_no  = document.getElementById('in_group').value.trim();
            const out_interface = document.getElementById('out_int').value.trim();
            const out_group_no = document.getElementById('out_group').value.trim();

            //ACL validation 
            if (selected_acl === 'Standard') {
                if (!st_deny_no || !st_deny_action || !st_deny_source) {
                    alert("All fields are required");
                    return;   
                }
            } 
            
            else if (selected_acl === 'Extended') {
                if (!ex_deny_no || !ex_deny_action || !ex_deny_protocol)
               {
                    alert("All Extended ACL fields are required");
                    return;   
                }
            }

            //Direction validation 
            if (selected_dir === 'in') {
                if (!in_interface || !in_group_no) {
                    alert("All inbound direction fields are required");
                    return;
                }
            } 
            
            else if (selected_dir === 'out') {
                if (!out_interface || !out_group_no) {
                    alert("All outbound direction fields are required");
                    return;
                }
            } 

            //ACL and Direction configuration objects
            const acl_config = {}
            const dir_config = {}

           //Looping through stored devices to create configuration for each device
            Object.keys(stored_devices).forEach((device_key) =>{
                //const device = stored_devices[device_key]

                if(selected_acl === "Standard"){
                    acl_config[device_key] = {
                        type : "Standard",
                        deny_no : document.getElementById('st-deny-no').value.trim(),
                        deny_action :  document.getElementById('st-deny').value.trim(),
                        deny_source: document.getElementById('st-deny-source').value,
                        permit_no : document.getElementById('st-permit-no').value.trim(),
                        permit_action :  document.getElementById('st-permit').value.trim(),
                        permit_source: document.getElementById('st-permit-source').value
                       
                    }

                }
                else if(selected_acl == "Extended"){
                    acl_config[device_key] = {
                        type : "Extended",
                        deny_no : document.getElementById('ex-deny-no').value.trim(),
                        deny_action :  document.getElementById('ex-deny').value.trim(),
                        deny_protocol :  document.getElementById('ex-deny-prot').value.trim(),
                        deny_port :  document.getElementById('ex-deny-port').value.trim(),
                        deny_source: document.getElementById('ex-deny-source').value,
                        deny_dest: document.getElementById('ex-deny-dest').value,
                        permit_no : document.getElementById('ex-permit-no').value.trim(),
                        permit_action :  document.getElementById('ex-permit').value.trim(),
                        permit_protocol :  document.getElementById('ex-permit-prot').value.trim(),
                        permit_port :  document.getElementById('ex-permit-port').value.trim(),
                        permit_source: document.getElementById('ex-permit-source').value,
                        permit_dest: document.getElementById('ex-permit-dest').value
                       
                    }
                }

                if(selected_dir === "in"){
                    dir_config[device_key] = {
                        direction : "in",
                        interface : document.getElementById('in_int').value.trim(),
                        group_no :  document.getElementById('in_group').value.trim()
                    }

                }

                if(selected_dir === "out"){
                    dir_config[device_key] = {
                        direction : "out",
                        interface : document.getElementById('out_int').value.trim(),
                        group_no :  document.getElementById('out_group').value.trim()
                    }

                }  
            })

            //Sending data via json to api endpoint for processing
            try{
                const response = await fetch('/api/acl_config', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        devices : stored_devices,
                        acl_config: acl_config,
                        dir_config: dir_config
                    })
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