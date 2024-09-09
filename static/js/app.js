document.addEventListener('DOMContentLoaded', () => {
    const clubsGrid = document.getElementById('clubs-grid');
    const searchInput = document.getElementById('search-input');
    const addClubForm = document.getElementById('add-club-form');
    const addClubModal = document.getElementById('add-club-modal');
    const openModalBtn = document.getElementById('open-modal-btn');
    const closeModalBtn = document.getElementById('close-modal-btn');

    // Fetch and display clubs
    function fetchClubs() {
        fetch('/clubs')
            .then(response => response.json())
            .then(clubs => {
                clubsGrid.innerHTML = '';
                clubs.forEach(club => {
                    const clubElement = createClubElement(club);
                    clubsGrid.appendChild(clubElement);
                });
            });
    }

    // Create club element
    function createClubElement(club) {
        const clubElement = document.createElement('div');
        clubElement.className = 'bg-white rounded-lg shadow-md p-4';
        clubElement.innerHTML = `
            <h3 class="text-xl font-semibold">${club.name}</h3>
            <p class="text-gray-600">${club.sport}</p>
            <p class="mt-2">${club.description}</p>
            <p class="text-sm text-gray-500">Org. Number: ${club.organizational_number || 'N/A'}</p>
            <div class="mt-4">
                <button class="bg-blue-500 text-white px-2 py-1 rounded mr-2 edit-btn" data-id="${club.id}">Edit</button>
                <button class="bg-red-500 text-white px-2 py-1 rounded delete-btn" data-id="${club.id}">Delete</button>
            </div>
        `;
        return clubElement;
    }

    // Search functionality
    searchInput.addEventListener('input', () => {
        const searchTerm = searchInput.value.toLowerCase();
        const clubElements = clubsGrid.children;
        Array.from(clubElements).forEach(clubElement => {
            const clubName = clubElement.querySelector('h3').textContent.toLowerCase();
            const clubSport = clubElement.querySelector('p').textContent.toLowerCase();
            if (clubName.includes(searchTerm) || clubSport.includes(searchTerm)) {
                clubElement.style.display = 'block';
            } else {
                clubElement.style.display = 'none';
            }
        });
    });

    // Add new club
    addClubForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(addClubForm);
        const clubData = Object.fromEntries(formData.entries());

        if (!clubData.organizational_number) {
            alert('Please provide an organizational number.');
            return;
        }

        fetch('/clubs', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(clubData),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(() => {
            fetchClubs();
            addClubForm.reset();
            addClubModal.classList.add('hidden');
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while adding the club. Please try again.');
        });
    });

    // Edit club
    clubsGrid.addEventListener('click', (e) => {
        if (e.target.classList.contains('edit-btn')) {
            const clubId = e.target.dataset.id;
            const clubElement = e.target.closest('.bg-white');
            const name = clubElement.querySelector('h3').textContent;
            const sport = clubElement.querySelector('p').textContent;
            const description = clubElement.querySelector('p:nth-child(3)').textContent;
            const organizationalNumber = clubElement.querySelector('p:nth-child(4)').textContent.replace('Org. Number: ', '');

            document.getElementById('edit-club-id').value = clubId;
            document.getElementById('edit-name').value = name;
            document.getElementById('edit-sport').value = sport;
            document.getElementById('edit-description').value = description;
            document.getElementById('edit-organizational-number').value = organizationalNumber === 'N/A' ? '' : organizationalNumber;

            addClubModal.classList.remove('hidden');
        }
    });

    // Update club
    addClubForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(addClubForm);
        const clubData = Object.fromEntries(formData.entries());
        const clubId = document.getElementById('edit-club-id').value;

        if (!clubData.organizational_number) {
            alert('Please provide an organizational number.');
            return;
        }

        if (clubId) {
            fetch(`/clubs/${clubId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(clubData),
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(() => {
                fetchClubs();
                addClubForm.reset();
                addClubModal.classList.add('hidden');
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while updating the club. Please try again.');
            });
        }
    });

    // Delete club
    clubsGrid.addEventListener('click', (e) => {
        if (e.target.classList.contains('delete-btn')) {
            const clubId = e.target.dataset.id;
            if (confirm('Are you sure you want to delete this club?')) {
                fetch(`/clubs/${clubId}`, {
                    method: 'DELETE',
                })
                .then(response => response.json())
                .then(() => {
                    fetchClubs();
                });
            }
        }
    });

    // Modal functionality
    openModalBtn.addEventListener('click', () => {
        addClubModal.classList.remove('hidden');
    });

    closeModalBtn.addEventListener('click', () => {
        addClubModal.classList.add('hidden');
        addClubForm.reset();
    });

    // Initial fetch
    fetchClubs();
});
