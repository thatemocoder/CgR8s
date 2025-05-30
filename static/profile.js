document.addEventListener('DOMContentLoaded', function() {
    const userData = JSON.parse(localStorage.getItem('userData')) || {};

    function displayUserData() {
        document.getElementById('profile-name').textContent = userData.name || 'Add Name';
        document.getElementById('profile-location').textContent = userData.location || 'Add Location';
        document.getElementById('profile-mobile').textContent = userData.mobile || 'Add Mobile';
        document.getElementById('profile-email').textContent = userData.email || 'Add Email';
        document.getElementById('profile-gender').textContent = userData.gender || 'Add Gender';
        document.getElementById('profile-birthday').textContent = userData.birthday || 'Add Birthday';
    }

    displayUserData();

    window.openEditModal = function(field) {
        const modal = document.getElementById('edit-modal');
        const fieldNameMap = {
            name: 'Name',
            location: 'Location',
            mobile: 'Mobile',
            email: 'Email',
            gender: 'Gender',
            birthday: 'Birthday'
        };
        document.getElementById('edit-field-name').textContent = fieldNameMap[field];
        document.getElementById('edit-field-value').value = userData[field] || '';
        modal.setAttribute('data-field', field);
        modal.style.display = 'block';
    }

    window.closeEditModal = function() {
        const modal = document.getElementById('edit-modal');
        modal.style.display = 'none';
    }

    window.saveEdit = function() {
        const modal = document.getElementById('edit-modal');
        const field = modal.getAttribute('data-field');
        const newValue = document.getElementById('edit-field-value').value;

        userData[field] = newValue;
        localStorage.setItem('userData', JSON.stringify(userData));
        displayUserData();
        closeEditModal();
    }

    // Handle file upload
    const uploadPhotoBtn = document.getElementById('upload-photo-btn');
    const uploadPhotoInput = document.getElementById('upload-photo-input');
    const profilePhoto = document.getElementById('profile-photo');

    if (uploadPhotoBtn && uploadPhotoInput && profilePhoto) {
        uploadPhotoBtn.addEventListener('click', function() {
            uploadPhotoInput.click();
        });

        uploadPhotoInput.addEventListener('change', function() {
            const file = uploadPhotoInput.files[0];
            const reader = new FileReader();
            reader.onloadend = function() {
                profilePhoto.src = reader.result;
            };
            if (file) {
                reader.readAsDataURL(file);
            }
        });
    }

    // // Mocked user data (assuming these fields exist in your HTML)
    // const user = {
    //     name: 'Vidit Shah',
    //     degree: 'B.Tech/B.E.',
    //     institute: 'Vellore Institute of Technology, Vellore',
    //     location: 'Ahmedabad',
    //     mobile: '7874482130',
    //     email: 'viditmanishshah@gmail.com',
    //     gender: '',
    //     birthday: ''
    // };

    // Assuming these IDs exist in your HTML for displaying user details
    document.getElementById('profile-name').innerText = user.name;
    document.getElementById('profile-degree').innerText = user.degree;
    document.getElementById('profile-institute').innerText = user.institute;
    document.getElementById('profile-location').innerText = user.location;
    document.getElementById('profile-mobile').innerText = user.mobile;
    document.getElementById('profile-email').innerText = user.email;

    // Add event listeners for the edit buttons
    document.querySelectorAll('.edit-btn').forEach(button => {
        button.addEventListener('click', function() {
            const field = this.getAttribute('data-field');
            openEditModal(field);
        });
    });

    // Additional edit handlers if needed
    document.getElementById('edit-gender').addEventListener('click', function() {
        openEditModal('gender');
    });

    document.getElementById('edit-birthday').addEventListener('click', function() {
        openEditModal('birthday');
    });

    // Career Preferences Modal handlers
    function openCareerPreferencesModal() {
        document.getElementById('career-preferences-modal').style.display = 'block';
    }

    function closeCareerPreferencesModal() {
        document.getElementById('career-preferences-modal').style.display = 'none';
    }

    function saveCareerPreferences() {
        const lookingFor = Array.from(document.querySelectorAll('input[name="lookingFor"]:checked')).map(el => el.value);
        const availability = document.querySelector('input[name="availability"]:checked').value;
        const locations = Array.from(document.getElementById('location-select').selectedOptions).map(option => option.value);

        const careerPreferences = {
            lookingFor,
            availability,
            locations
        };

        localStorage.setItem('careerPreferences', JSON.stringify(careerPreferences));
        closeCareerPreferencesModal();
    }

    const careerPreferencesBtn = document.getElementById('career-preferences-btn');
    if (careerPreferencesBtn) {
        careerPreferencesBtn.addEventListener('click', openCareerPreferencesModal);
    }

    document.getElementById('save-career-preferences-btn').addEventListener('click', saveCareerPreferences);
    document.getElementById('close-career-preferences-btn').addEventListener('click', closeCareerPreferencesModal);
});
