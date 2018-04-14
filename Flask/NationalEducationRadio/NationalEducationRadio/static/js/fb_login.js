/**
 * Created by Jessie on 2018/02/26
 */

// run FB.log and check response.status == 'connected'
async function FBloginAsync(){
    return new Promise((resolve,reject)=>{
        FB.login(response=>{
            if(response.status == 'connected')resolve(response)
            else reject(response)
        })
    })
}

async function FBDetailAsync(){
    return new Promise((resolve,reject)=>{
        FB.api('/me', {fields: 'id,name,email'},response=>{
            if('error' in response) reject(response)
            else resolve(response)
        })
    })
}

//jquery ajax with async interface
async function ajaxAsync(...args){
    return new Promise(
        (resolve,reject)=>{
            $.ajax(...args)
            .done(resolve)
            .fail(reject)
        }
    )
}

async function checkFBlogin(){
    //turn exception to alert
    try {await _checkFBlogin()}
    catch(e){
        alert('login fail'); 
        throw e;
    }
}

async function _checkFBlogin() {
    response = await FBloginAsync()
    user_detail =  await FBDetailAsync()
    let {userID,accessToken}=response.authResponse
    let {name,email}=user_detail

    let data = {
        userID,
        accessToken,
        userName: name,
        userEmail: email
    }
    
    let data_json = JSON.stringify(data);
    console.log(data_json)

    await ajaxAsync({
        url: 'API_FB_login',
        type: "POST",
        data: data_json,
        dataType: "json",
        async: false,
        contentType: "application/json"
    })
    
    window.location.replace('.')
}