<script>
  import { onMount } from 'svelte';
  import { 
    User, 
    Briefcase, 
    GraduationCap, 
    FileText, 
    Eye, 
    EyeOff, 
    Upload, 
    Save, 
    Plus, 
    Trash2,
    CheckCircle,
    AlertCircle
  } from '@lucide/svelte';

  let currentStep = 0;
  let profileVisible = true;
  let resumeFile = null;
  let profileCompletion = 0;

  // Form data
  let personalInfo = {
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    location: '',
    summary: ''
  };

  let professionalDetails = {
    skills: [],
    newSkill: '',
    linkedIn: '',
    portfolio: '',
    currentRole: '',
    yearsExperience: ''
  };

  let education = [{
    degree: '',
    institution: '',
    year: '',
    gpa: ''
  }];

  let experience = [{
    jobTitle: '',
    company: '',
    startDate: '',
    endDate: '',
    current: false,
    description: ''
  }];

  // Validation errors
  let errors = {};

  const steps = [
    { id: 0, title: 'Personal Info', icon: User },
    { id: 1, title: 'Professional', icon: Briefcase },
    { id: 2, title: 'Education', icon: GraduationCap },
    { id: 3, title: 'Experience', icon: FileText }
  ];

  function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  function validatePhone(phone) {
    return /^\+?[\d\s-()]+$/.test(phone);
  }

  function validateField(field, value, type = 'text') {
    if (!value || value.trim() === '') {
      return 'This field is required';
    }
    
    if (type === 'email' && !validateEmail(value)) {
      return 'Please enter a valid email address';
    }
    
    if (type === 'phone' && !validatePhone(value)) {
      return 'Please enter a valid phone number';
    }
    
    return null;
  }

  function addSkill() {
    if (professionalDetails.newSkill.trim()) {
      professionalDetails.skills = [...professionalDetails.skills, professionalDetails.newSkill.trim()];
      professionalDetails.newSkill = '';
    }
  }

  function removeSkill(index) {
    professionalDetails.skills = professionalDetails.skills.filter((_, i) => i !== index);
  }

  function addEducation() {
    education = [...education, { degree: '', institution: '', year: '', gpa: '' }];
  }

  function removeEducation(index) {
    if (education.length > 1) {
      education = education.filter((_, i) => i !== index);
    }
  }

  function addExperience() {
    experience = [...experience, { 
      jobTitle: '', 
      company: '', 
      startDate: '', 
      endDate: '', 
      current: false, 
      description: '' 
    }];
  }

  function removeExperience(index) {
    if (experience.length > 1) {
      experience = experience.filter((_, i) => i !== index);
    }
  }

  function handleResumeUpload(event) {
    const file = event.target.files[0];
    if (file) {
      if (file.type !== 'application/pdf') {
        errors.resume = 'Please upload a PDF file';
        return;
      }
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
        errors.resume = 'File size must be less than 5MB';
        return;
      }
      resumeFile = file;
      errors.resume = null;
    }
  }

  function calculateCompletion() {
    let completed = 0;
    let total = 0;

    // Personal info (6 fields)
    const personalFields = Object.values(personalInfo);
    total += personalFields.length;
    completed += personalFields.filter(field => field && field.trim()).length;

    // Professional details (4 required fields + skills)
    total += 4;
    if (professionalDetails.currentRole.trim()) completed++;
    if (professionalDetails.yearsExperience.trim()) completed++;
    if (professionalDetails.linkedIn.trim()) completed++;
    if (professionalDetails.skills.length > 0) completed++;

    // Education (at least one complete entry)
    total += 1;
    if (education.some(edu => edu.degree && edu.institution && edu.year)) completed++;

    // Experience (at least one complete entry)
    total += 1;
    if (experience.some(exp => exp.jobTitle && exp.company && exp.startDate)) completed++;

    // Resume upload
    total += 1;
    if (resumeFile) completed++;

    profileCompletion = Math.round((completed / total) * 100);
  }

  async function saveProfile() {
    try {
      const formData = new FormData();
      formData.append('personalInfo', JSON.stringify(personalInfo));
      formData.append('professionalDetails', JSON.stringify(professionalDetails));
      formData.append('education', JSON.stringify(education));
      formData.append('experience', JSON.stringify(experience));
      formData.append('profileVisible', profileVisible);
      
      if (resumeFile) {
        formData.append('resume', resumeFile);
      }

      // TODO: Replace with actual API call
      console.log('Saving profile...');
      // const response = await fetch('/api/profile', {
      //   method: 'POST',
      //   body: formData
      // });
      
      alert('Profile saved successfully!');
    } catch (error) {
      console.error('Error saving profile:', error);
      alert('Error saving profile. Please try again.');
    }
  }

  $: calculateCompletion();
</script>

<div class="min-h-screen bg-gray-50 py-8">
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Header -->
    <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
      <div class="flex items-center justify-between mb-4">
        <h1 class="text-3xl font-bold text-gray-900">Profile Management</h1>
        <div class="flex items-center space-x-4">
          <div class="flex items-center space-x-2">
            <span class="text-sm text-gray-600">Profile Visibility</span>
            <button
              onclick={() => profileVisible = !profileVisible}
              class="flex items-center space-x-1 text-sm"
            >
              {#if profileVisible}
                <Eye class="w-4 h-4 text-green-500" />
                <span class="text-green-600">Public</span>
              {:else}
                <EyeOff class="w-4 h-4 text-gray-500" />
                <span class="text-gray-600">Private</span>
              {/if}
            </button>
          </div>
        </div>
      </div>

      <!-- Progress Bar -->
      <div class="mb-6">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium text-gray-700">Profile Completion</span>
          <span class="text-sm font-medium text-blue-600">{profileCompletion}%</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div 
            class="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style="width: {profileCompletion}%"
          ></div>
        </div>
      </div>

      <!-- Step Navigation -->
      <div class="flex space-x-1 mb-6 overflow-x-auto">
        {#each steps as step, index}
          <button
            onclick={() => currentStep = index}
            class="flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap
              {currentStep === index 
                ? 'bg-blue-100 text-blue-700 border border-blue-200' 
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'}"
          >
            <svelte:component this={step.icon} class="w-4 h-4" />
            <span class="hidden sm:inline">{step.title}</span>
          </button>
        {/each}
      </div>
    </div>

    <!-- Form Content -->
    <div class="bg-white rounded-lg shadow-sm p-6">
      {#if currentStep === 0}
        <!-- Personal Information -->
        <div class="space-y-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">Personal Information</h2>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">First Name *</label>
              <input
                bind:value={personalInfo.firstName}
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter your first name"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Last Name *</label>
              <input
                bind:value={personalInfo.lastName}
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter your last name"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Email *</label>
              <input
                bind:value={personalInfo.email}
                type="email"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="your.email@example.com"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Phone *</label>
              <input
                bind:value={personalInfo.phone}
                type="tel"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="+1 (555) 123-4567"
              />
            </div>
            
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-2">Location</label>
              <input
                bind:value={personalInfo.location}
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="City, State, Country"
              />
            </div>
            
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-2">Professional Summary</label>
              <textarea
                bind:value={personalInfo.summary}
                rows="4"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Brief summary of your professional background and career objectives..."
              ></textarea>
            </div>
          </div>
        </div>

      {:else if currentStep === 1}
        <!-- Professional Details -->
        <div class="space-y-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">Professional Details</h2>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Current Role</label>
              <input
                bind:value={professionalDetails.currentRole}
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., Software Engineer"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Years of Experience</label>
              <select
                bind:value={professionalDetails.yearsExperience}
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select experience</option>
                <option value="0-1">0-1 years</option>
                <option value="1-3">1-3 years</option>
                <option value="3-5">3-5 years</option>
                <option value="5-10">5-10 years</option>
                <option value="10+">10+ years</option>
              </select>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">LinkedIn Profile</label>
              <input
                bind:value={professionalDetails.linkedIn}
                type="url"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="https://linkedin.com/in/yourprofile"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Portfolio Website</label>
              <input
                bind:value={professionalDetails.portfolio}
                type="url"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="https://yourportfolio.com"
              />
            </div>
          </div>
          
          <!-- Skills Section -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Skills</label>
            <div class="flex space-x-2 mb-3">
              <input
                bind:value={professionalDetails.newSkill}
                type="text"
                class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Add a skill..."
                onkeypress={(e) => e.key === 'Enter' && addSkill()}
              />
              <button
                onclick={addSkill}
                class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <Plus class="w-4 h-4" />
              </button>
            </div>
            
            <div class="flex flex-wrap gap-2">
              {#each professionalDetails.skills as skill, index}
                <span class="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                  {skill}
                  <button
                    onclick={() => removeSkill(index)}
                    class="ml-2 text-blue-600 hover:text-blue-800"
                  >
                    <Trash2 class="w-3 h-3" />
                  </button>
                </span>
              {/each}
            </div>
          </div>
        </div>

      {:else if currentStep === 2}
        <!-- Education -->
        <div class="space-y-6">
          <div class="flex items-center justify-between">
            <h2 class="text-xl font-semibold text-gray-900">Education</h2>
            <button
              onclick={addEducation}
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 flex items-center space-x-2"
            >
              <Plus class="w-4 h-4" />
              <span>Add Education</span>
            </button>
          </div>
          
          {#each education as edu, index}
            <div class="border border-gray-200 rounded-lg p-4 space-y-4">
              <div class="flex items-center justify-between">
                <h3 class="text-lg font-medium text-gray-900">Education {index + 1}</h3>
                {#if education.length > 1}
                  <button
                    onclick={() => removeEducation(index)}
                    class="text-red-600 hover:text-red-800"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                {/if}
              </div>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Degree *</label>
                  <input
                    bind:value={edu.degree}
                    type="text"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., Bachelor of Science"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Institution *</label>
                  <input
                    bind:value={edu.institution}
                    type="text"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="University/College name"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Graduation Year *</label>
                  <input
                    bind:value={edu.year}
                    type="number"
                    min="1950"
                    max="2030"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="2023"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">GPA (Optional)</label>
                  <input
                    bind:value={edu.gpa}
                    type="text"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="3.8/4.0"
                  />
                </div>
              </div>
            </div>
          {/each}
        </div>

      {:else if currentStep === 3}
        <!-- Experience -->
        <div class="space-y-6">
          <div class="flex items-center justify-between">
            <h2 class="text-xl font-semibold text-gray-900">Work Experience</h2>
            <button
              onclick={addExperience}
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 flex items-center space-x-2"
            >
              <Plus class="w-4 h-4" />
              <span>Add Experience</span>
            </button>
          </div>
          
          {#each experience as exp, index}
            <div class="border border-gray-200 rounded-lg p-4 space-y-4">
              <div class="flex items-center justify-between">
                <h3 class="text-lg font-medium text-gray-900">Experience {index + 1}</h3>
                {#if experience.length > 1}
                  <button
                    onclick={() => removeExperience(index)}
                    class="text-red-600 hover:text-red-800"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                {/if}
              </div>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Job Title *</label>
                  <input
                    bind:value={exp.jobTitle}
                    type="text"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., Software Engineer"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Company *</label>
                  <input
                    bind:value={exp.company}
                    type="text"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Company name"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Start Date *</label>
                  <input
                    bind:value={exp.startDate}
                    type="month"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">End Date</label>
                  <input
                    bind:value={exp.endDate}
                    type="month"
                    disabled={exp.current}
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                  />
                  <label class="flex items-center mt-2">
                    <input
                      bind:checked={exp.current}
                      type="checkbox"
                      class="mr-2"
                    />
                    <span class="text-sm text-gray-600">I currently work here</span>
                  </label>
                </div>
                
                <div class="md:col-span-2">
                  <label class="block text-sm font-medium text-gray-700 mb-2">Job Description</label>
                  <textarea
                    bind:value={exp.description}
                    rows="3"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Describe your responsibilities and achievements..."
                  ></textarea>
                </div>
              </div>
            </div>
          {/each}
          
          <!-- Resume Upload -->
          <div class="border-t pt-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Resume Upload</h3>
            <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <Upload class="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <div class="space-y-2">
                <p class="text-sm text-gray-600">Upload your resume (PDF only, max 5MB)</p>
                <input
                  type="file"
                  accept=".pdf"
                  onchange={handleResumeUpload}
                  class="hidden"
                  id="resume-upload"
                />
                <label
                  for="resume-upload"
                  class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 cursor-pointer"
                >
                  Choose File
                </label>
              </div>
              {#if resumeFile}
                <div class="mt-4 flex items-center justify-center space-x-2 text-green-600">
                  <CheckCircle class="w-4 h-4" />
                  <span class="text-sm">{resumeFile.name}</span>
                </div>
              {/if}
              {#if errors.resume}
                <div class="mt-2 flex items-center justify-center space-x-2 text-red-600">
                  <AlertCircle class="w-4 h-4" />
                  <span class="text-sm">{errors.resume}</span>
                </div>
              {/if}
            </div>
          </div>
        </div>
      {/if}

      <!-- Navigation Buttons -->
      <div class="flex justify-between mt-8 pt-6 border-t">
        <button
          onclick={() => currentStep = Math.max(0, currentStep - 1)}
          disabled={currentStep === 0}
          class="px-4 py-2 text-gray-600 bg-gray-100 rounded-md hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Previous
        </button>
        
        <div class="flex space-x-3">
          {#if currentStep < steps.length - 1}
            <button
              onclick={() => currentStep = Math.min(steps.length - 1, currentStep + 1)}
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Next
            </button>
          {:else}
            <button
              onclick={saveProfile}
              class="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 flex items-center space-x-2"
            >
              <Save class="w-4 h-4" />
              <span>Save Profile</span>
            </button>
          {/if}
        </div>
      </div>
    </div>
  </div>
</div>