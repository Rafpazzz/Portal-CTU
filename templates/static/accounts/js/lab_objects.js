(function () {
    const page = document.querySelector('.lab-page');
    const form = document.getElementById('lab-object-form');
    const formTitle = document.getElementById('lab-form-title');
    const tableBody = document.getElementById('lab-objects-table');
    const statusBox = document.getElementById('lab-status');
    const searchForm = document.getElementById('lab-search-form');
    const searchInput = document.getElementById('lab-search-input');
    const resetButton = document.getElementById('reset-form-button');
    const csvLink = document.getElementById('export-csv-link');
    const pdfLink = document.getElementById('export-pdf-link');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    let currentSearch = '';

    function showStatus(message, type) {
        statusBox.textContent = message || '';
        statusBox.className = message ? `status-message ${type || 'info'}` : 'status-message';
    }

    function clearErrors() {
        document.querySelectorAll('.field-error').forEach((item) => {
            item.textContent = '';
        });
    }

    function setErrors(errors) {
        clearErrors();
        Object.entries(errors || {}).forEach(([field, messages]) => {
            const target = document.querySelector(`[data-error-for="${field}"]`);
            if (target) {
                target.textContent = messages.join(' ');
            }
        });
    }

    function validateForm() {
        clearErrors();
        const nome = form.nome.value.trim();
        const condicao = form.condicao.value;
        const quantidade = Number(form.quantidade.value);
        const errors = {};

        if (!nome) {
            errors.nome = ['Informe o nome do objeto.'];
        }

        if (!condicao) {
            errors.condicao = ['Selecione a condicao.'];
        }

        if (!Number.isInteger(quantidade) || quantidade < 0) {
            errors.quantidade = ['Informe uma quantidade inteira maior ou igual a zero.'];
        }

        setErrors(errors);
        return Object.keys(errors).length === 0;
    }

    function objectUrl(id) {
        return `${page.dataset.apiUrl}${id}/`;
    }

    function updateExportLinks() {
        const query = currentSearch ? `?q=${encodeURIComponent(currentSearch)}` : '';
        csvLink.href = `${page.dataset.csvUrl}${query}`;
        pdfLink.href = `${page.dataset.pdfUrl}${query}`;
    }

    function resetForm() {
        form.reset();
        form.object_id.value = '';
        form.quantidade.value = '0';
        formTitle.textContent = 'Adicionar objeto';
        clearErrors();
    }

    function fillForm(item) {
        form.object_id.value = item.id;
        form.nome.value = item.nome;
        form.condicao.value = item.condicao;
        form.quantidade.value = item.quantidade;
        form.descricao.value = item.descricao || '';
        formTitle.textContent = `Editar objeto #${item.id}`;
        clearErrors();
        window.scrollTo({ top: form.offsetTop - 90, behavior: 'smooth' });
    }

    function escapeHtml(value) {
        return String(value || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    function renderObjects(objects) {
        if (!objects.length) {
            tableBody.innerHTML = '<tr><td colspan="6">Nenhum objeto encontrado.</td></tr>';
            return;
        }

        tableBody.innerHTML = objects.map((item) => `
            <tr data-object-id="${item.id}">
                <td>${item.id}</td>
                <td>${escapeHtml(item.nome)}</td>
                <td>${escapeHtml(item.condicao_label)}</td>
                <td>${item.quantidade}</td>
                <td>${escapeHtml(item.descricao)}</td>
                <td class="table-actions">
                    <button type="button" class="table-button edit-object" data-id="${item.id}">Editar</button>
                    <button type="button" class="table-button danger-text delete-object" data-id="${item.id}">Remover</button>
                </td>
            </tr>
        `).join('');
    }

    async function loadObjects() {
        const query = currentSearch ? `?q=${encodeURIComponent(currentSearch)}` : '';
        const response = await fetch(`${page.dataset.apiUrl}${query}`, {
            headers: { Accept: 'application/json' },
        });

        if (!response.ok) {
            showStatus('Nao foi possivel carregar os objetos.', 'error');
            return;
        }

        const data = await response.json();
        renderObjects(data.objects);
        updateExportLinks();
    }

    async function saveObject(event) {
        event.preventDefault();

        if (!validateForm()) {
            showStatus('Corrija os campos destacados antes de salvar.', 'error');
            return;
        }

        const id = form.object_id.value;
        const url = id ? objectUrl(id) : page.dataset.apiUrl;
        const payload = {
            nome: form.nome.value.trim(),
            condicao: form.condicao.value,
            quantidade: form.quantidade.value,
            descricao: form.descricao.value.trim(),
        };

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                Accept: 'application/json',
            },
            body: JSON.stringify(payload),
        });

        const data = await response.json();

        if (!response.ok) {
            setErrors(data.errors);
            showStatus('Nao foi possivel salvar o objeto.', 'error');
            return;
        }

        resetForm();
        showStatus(id ? 'Objeto atualizado com sucesso.' : 'Objeto adicionado com sucesso.', 'success');
        await loadObjects();
    }

    async function loadObjectForEdit(id) {
        const response = await fetch(objectUrl(id), {
            headers: { Accept: 'application/json' },
        });

        if (!response.ok) {
            showStatus('Objeto nao encontrado.', 'error');
            return;
        }

        const data = await response.json();
        fillForm(data.object);
    }

    async function deleteObject(id) {
        const confirmed = window.confirm('Remover este objeto do laboratorio?');
        if (!confirmed) {
            return;
        }

        const response = await fetch(objectUrl(id), {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrfToken,
                Accept: 'application/json',
            },
        });

        if (!response.ok) {
            showStatus('Nao foi possivel remover o objeto.', 'error');
            return;
        }

        showStatus('Objeto removido com sucesso.', 'success');
        await loadObjects();
    }

    form.addEventListener('submit', saveObject);
    resetButton.addEventListener('click', resetForm);

    searchForm.addEventListener('submit', (event) => {
        event.preventDefault();
        currentSearch = searchInput.value.trim();
        loadObjects();
    });

    tableBody.addEventListener('click', (event) => {
        const editButton = event.target.closest('.edit-object');
        const deleteButton = event.target.closest('.delete-object');

        if (editButton) {
            loadObjectForEdit(editButton.dataset.id);
        }

        if (deleteButton) {
            deleteObject(deleteButton.dataset.id);
        }
    });

    loadObjects();
})();
