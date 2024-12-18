/* global Vue, lucide, toastr */

const app = Vue.createApp({
    delimiters: ['${', '}'],
    data() {
      return {
        apiKeys: [],
        loading: true,
        showCreateModal: false,
        showDeleteModal: false,
        newKeyDescription: '',
        visibleKeys: {},
        keyToDelete: null,
        roleDescriptions: {
          default: 'Access to all public endpoints',
          cms: 'Access to CMS system endpoints',
          '*': 'Wildcard role with access to all endpoints',
          // Add any other role descriptions here
        },
        copyingStates: {},
      }
    },
    watch: {
      showCreateModal(newVal) {
        if (newVal) {
          this.$nextTick(() => {
            document.getElementById('keyDescription')?.focus();
            lucide.createIcons();
          });
        } else {
          this.newKeyDescription = '';
        }
      },
      showDeleteModal(newVal) {
        if (newVal) {
          this.$nextTick(() => {
            lucide.createIcons();
          });
        }
      }
    },
    methods: {
      getRoleDescription(role) {
        return this.roleDescriptions[role.toLowerCase()] || role;
      },
  
      async fetchApiKeys() {
        this.loading = true;
        try {
          const response = await fetch('/api/me/api-keys');
          const result = await response.json();
  
          if (result.status === 'success' && Array.isArray(result.data)) {
            this.apiKeys = result.data;
          } else {
            toastr.error('Invalid response format');
          }
        } catch (err) {
          console.error(err);
          toastr.error('Failed to fetch API keys');
        } finally {
          this.loading = false;
          this.$nextTick(() => {
            lucide.createIcons();
            requestAnimationFrame(() => {
              document.querySelectorAll('.fade-in').forEach((el) => el.classList.add('visible'));
            });
          });
        }
      },
  
      formatDate(timestamp) {
        if (!timestamp) return 'Never';
        const date = new Date(timestamp * 1000);
        if (isNaN(date.getTime())) return 'Invalid date';
  
        return date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
      },
  
      toggleKeyVisibility(keyId) {
        this.visibleKeys[keyId] = !this.visibleKeys[keyId];
        this.$nextTick(() => lucide.createIcons());
      },
  
      async copyKey(keyId) {
        // If already in a copying state, return
        if (this.copyingStates[keyId]) return;
        
        try {
          await navigator.clipboard.writeText(keyId);
          this.copyingStates[keyId] = 'success';
        } catch (err) {
          console.error(err);
          this.copyingStates[keyId] = 'error';
        }
        
        // Update icons
        this.$nextTick(() => lucide.createIcons());
        
        // Reset after animation
        setTimeout(() => {
          this.copyingStates[keyId] = null;
          // Update icons again after reset
          this.$nextTick(() => lucide.createIcons());
        }, 1500);
      },
  
      async createKey() {
        const description = this.newKeyDescription.trim();
        if (!description) {
          toastr.error('Please provide a description for your API key');
          return;
        }
  
        try {
          const response = await fetch('/api/me/api-keys', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ description }),
          });
  
          const result = await response.json();
  
          if (result.status === 'success') {
            this.showCreateModal = false;
            this.newKeyDescription = '';
            toastr.success('API key created successfully');
            this.fetchApiKeys();
          } else {
            toastr.error(result.message || 'Failed to create API key');
          }
        } catch (err) {
          console.error(err);
          toastr.error('Failed to create API key');
        }
      },
  
      openDeleteModal(key) {
        this.keyToDelete = key;
        this.showDeleteModal = true;
      },
  
      closeDeleteModal() {
        const modal = document.querySelector('.modal.active');
        modal?.classList.add('fade-out');
        
        setTimeout(() => {
          this.showDeleteModal = false;
          this.keyToDelete = null;
          modal?.classList.remove('fade-out');
        }, 200);
      },
  
      async confirmDelete() {
        if (!this.keyToDelete) return;
  
        try {
          const response = await fetch(`/api/me/api-keys/${this.keyToDelete._id}`, {
            method: 'DELETE',
          });
  
          const result = await response.json();
  
          if (result.status === 'success') {
            toastr.success('API key deleted successfully');
            this.fetchApiKeys();
            this.closeDeleteModal();
          } else {
            toastr.error(result.message || 'Failed to delete API key');
          }
        } catch (err) {
          console.error(err);
          toastr.error('Failed to delete API key');
        }
      },
  
      handleEscapeKey(event) {
        if (event.key === 'Escape') {
          if (this.showDeleteModal) {
            this.closeDeleteModal();
          } else if (this.showCreateModal) {
            this.showCreateModal = false;
          }
        }
      }
    },
    mounted() {
      this.fetchApiKeys();
      document.addEventListener('keydown', this.handleEscapeKey);
    },
    beforeUnmount() {
      document.removeEventListener('keydown', this.handleEscapeKey);
    }
  }).mount('#app');