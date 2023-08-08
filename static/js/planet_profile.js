const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value

// 팔로잉
if (document.querySelector('.follow-form')) {

  const followForm = document.querySelector('.follow-form')
  followForm.addEventListener('submit', (e) => {
    e.preventDefault()
    const userPk = e.target.dataset.userPk
    const planetName = e.target.dataset.planetName
    
    axios({
      post:'post',
      url:`/planets/${planetName}/follow/${userPk}/`,
      headers: {'X-CSRFToken': csrftoken,}
    })
    .then((response) => {
      const isFollowed = response.data.is_followed
      const followBtn = document.querySelector('.follow-btn')
      
      const followerCountData = response.data.follower_count
      const followerCountTag = document.querySelector('.follower-count')

      const followerListDiv = document.querySelector('.follower-list')

      if(isFollowed === true) {
        followBtn.value = 'following'
        const newFollowerField = document.createElement('div')
        newFollowerField.innerHTML = `
        <div class="my-2 flex p-2 text-ml border-0 rounded-md bg-[#181A20]" id="follower-${response.data.from_user_pk}">
        <img id="imgDino" src="https://mblogthumb-phinf.pstatic.net/MjAxODEwMjNfNjAg/MDAxNTQwMjg2OTk2NTcw.mfWKPtzKVO1mJaBBIFKIkVBlMQQIF1Vc-yrlbbGaoP0g.KNJWAgMmhsfQrZI3n0UT-LMi_qpHAZls4qPMvbNaJBcg.GIF.chingguhl/Spinner-1s-200px.gif?type=w800" alt="no_image" class="inline-block" width="40">
        <p class="text-slate-200 text-ml flex items-center ml-4">${response.data.from_user_name}</p>
        </div>`
        followerListDiv.appendChild(newFollowerField)
      }
      else {
        followBtn.value = 'follow'
        const followerList = document.querySelector(`#follower-${response.data.from_user_pk}`)
        followerList.remove()
      }
      followerCountTag.innerHTML = followerCountData
    })
    .catch((error) => {
      console.log(error.response)
    })
  })
}