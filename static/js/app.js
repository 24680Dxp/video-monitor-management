const { createApp } = Vue;

const API_BASE = '/api';

Vue.createApp({
    delimiters: ['[[', ']]'],
    data() {
        return {
            isLoggedIn: false,
            currentView: 'dashboard',
            token: localStorage.getItem('token'),
            user: null,
            loading: false,
            currentTime: '',
            showModal: false,
            modalTitle: '',
            modalContent: '',
            showToast: false,
            toastMessage: '',
            toastType: 'info',

            viewTitles: {
                dashboard: '仪表盘',
                workorders: '工单管理',
                projects: '项目管理',
                points: '点位管理',
                materials: '物资管理',
                reports: '统计报表'
            },

            statusNames: {
                pending: '待处理',
                processing: '处理中',
                completed: '已完成',
                cancelled: '已取消'
            },

            typeNames: {
                install: '安装',
                maintenance: '维护',
                inspection: '巡检',
                fault: '故障'
            },

            priorityNames: {
                low: '低',
                normal: '普通',
                high: '高',
                urgent: '紧急'
            },

            projectStatusNames: {
                active: '进行中',
                completed: '已完成',
                suspended: '已暂停'
            },

            loginForm: {
                username: '',
                password: ''
            },

            dashboardData: {
                kpi: {},
                workorder_trend: [],
                by_status: [],
                by_type: [],
                recent_workorders: []
            },

            workorders: [],
            workorderPage: 1,
            workorderTotalPages: 1,
            workorderFilters: {
                keyword: '',
                status: '',
                type: ''
            },

            projects: [],
            projectPage: 1,
            projectTotalPages: 1,
            projectFilters: {
                keyword: '',
                status: ''
            },
            projectList: [],

            points: [],
            pointPage: 1,
            pointTotalPages: 1,
            pointFilters: {
                keyword: '',
                project_id: ''
            },

            materials: [],
            materialFilters: {
                keyword: '',
                category: ''
            },
            categories: [],
            inbounds: [],
            outbounds: [],
            inventoryItems: [],
            inventoryStats: {
                total_count: 0,
                total_value: 0
            },
            materialTab: 'list',

            reportFilters: {
                start_date: '',
                end_date: '',
                project_id: ''
            },
            reportStats: {
                total: 0,
                pending: 0,
                processing: 0,
                completed: 0,
                completion_rate: 0
            },
            projectStats: {
                total_projects: 0,
                active_projects: 0,
                projects: []
            },
            materialStats: {
                total_materials: 0,
                total_stock_value: 0,
                low_stock_count: 0
            },
            engineerStats: []
        };
    },

    computed: {
        maxTrendCount() {
            if (!this.dashboardData.workorder_trend || this.dashboardData.workorder_trend.length === 0) return 1;
            return Math.max(...this.dashboardData.workorder_trend.map(t => t.count), 1);
        }
    },

    mounted() {
        if (this.token) {
            this.checkAuth();
        }
        this.updateTime();
        setInterval(this.updateTime, 1000);
    },

    methods: {
        async request(url, options = {}) {
            const headers = {
                'Content-Type': 'application/json',
                ...options.headers
            };

            if (this.token) {
                headers['Authorization'] = `Bearer ${this.token}`;
            }

            try {
                const response = await fetch(`${API_BASE}${url}`, {
                    ...options,
                    headers
                });

                const data = await response.json();

                if (!response.ok) {
                    if (response.status === 401) {
                        this.handleLogout();
                    }
                    throw new Error(data.message || '请求失败');
                }

                return data;
            } catch (error) {
                console.error('Request error:', error);
                throw error;
            }
        },

        async checkAuth() {
            try {
                const res = await this.request('/auth/current-user');
                this.user = res.data;
                this.isLoggedIn = true;
                this.loadDashboard();
            } catch (error) {
                this.handleLogout();
            }
        },

        async handleLogin() {
            this.loading = true;
            try {
                const res = await this.request('/auth/login', {
                    method: 'POST',
                    body: JSON.stringify(this.loginForm)
                });

                this.token = res.data.token;
                this.user = res.data.user;
                localStorage.setItem('token', this.token);
                this.isLoggedIn = true;
                this.loginForm = { username: '', password: '' };
                this.showToastMessage('登录成功', 'success');
                this.loadDashboard();
            } catch (error) {
                this.showToastMessage(error.message || '登录失败', 'error');
            } finally {
                this.loading = false;
            }
        },

        handleLogout() {
            this.token = null;
            this.user = null;
            this.isLoggedIn = false;
            localStorage.removeItem('token');
            this.currentView = 'dashboard';
        },

        updateTime() {
            const now = new Date();
            this.currentTime = now.toLocaleString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        },

        formatDate(dateStr) {
            if (!dateStr) return '-';
            return new Date(dateStr).toLocaleDateString('zh-CN');
        },

        formatDateTime(dateStr) {
            if (!dateStr) return '-';
            return new Date(dateStr).toLocaleString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        },

        showToastMessage(message, type = 'info') {
            this.toastMessage = message;
            this.toastType = type;
            this.showToast = true;
            setTimeout(() => {
                this.showToast = false;
            }, 3000);
        },

        async loadDashboard() {
            try {
                const res = await this.request('/reports/dashboard');
                this.dashboardData = {
                    ...res.data,
                    kpi: res.data.kpi || {},
                    today_workorders: res.data.kpi?.today_workorders || 0,
                    pending_workorders: res.data.kpi?.pending_workorders || 0,
                    active_projects: res.data.kpi?.active_projects || 0,
                    low_stock_materials: res.data.kpi?.low_stock_materials || 0
                };
                this.dashboardData.total = this.dashboardData.by_status.reduce((sum, s) => sum + s.count, 0);
            } catch (error) {
                console.error('Load dashboard error:', error);
            }
        },

        async loadWorkorders() {
            try {
                const params = new URLSearchParams({
                    page: this.workorderPage,
                    per_page: 20,
                    ...this.workorderFilters
                });
                Object.keys(params).forEach(key => {
                    if (!params[key]) params.delete(key);
                });

                const res = await this.request(`/workorders?${params}`);
                this.workorders = res.data.items;
                this.workorderTotalPages = res.data.pages;
            } catch (error) {
                this.showToastMessage('加载工单失败', 'error');
            }
        },

        changeWorkorderPage(page) {
            if (page >= 1 && page <= this.workorderTotalPages) {
                this.workorderPage = page;
                this.loadWorkorders();
            }
        },

        async loadProjects() {
            try {
                const params = new URLSearchParams({
                    page: this.projectPage,
                    per_page: 20,
                    ...this.projectFilters
                });
                Object.keys(params).forEach(key => {
                    if (!params[key]) params.delete(key);
                });

                const res = await this.request(`/projects?${params}`);
                this.projects = res.data.items;
                this.projectTotalPages = res.data.pages;
            } catch (error) {
                this.showToastMessage('加载项目失败', 'error');
            }
        },

        changeProjectPage(page) {
            if (page >= 1 && page <= this.projectTotalPages) {
                this.projectPage = page;
                this.loadProjects();
            }
        },

        async loadProjectList() {
            try {
                const res = await this.request('/projects?per_page=100');
                this.projectList = res.data.items;
            } catch (error) {
                console.error('Load project list error:', error);
            }
        },

        async loadPoints() {
            try {
                const params = new URLSearchParams({
                    page: this.pointPage,
                    per_page: 20,
                    ...this.pointFilters
                });
                Object.keys(params).forEach(key => {
                    if (!params[key]) params.delete(key);
                });

                const res = await this.request(`/points?${params}`);
                this.points = res.data.items;
                this.pointTotalPages = res.data.pages;
            } catch (error) {
                this.showToastMessage('加载点位失败', 'error');
            }
        },

        changePointPage(page) {
            if (page >= 1 && page <= this.pointTotalPages) {
                this.pointPage = page;
                this.loadPoints();
            }
        },

        async loadMaterials() {
            try {
                const params = new URLSearchParams({
                    page: 1,
                    per_page: 50,
                    ...this.materialFilters
                });
                Object.keys(params).forEach(key => {
                    if (!params[key]) params.delete(key);
                });

                const res = await this.request(`/materials?${params}`);
                this.materials = res.data.items;

                const catRes = await this.request('/materials/categories');
                this.categories = catRes.data;
            } catch (error) {
                this.showToastMessage('加载物资失败', 'error');
            }
        },

        async loadInbounds() {
            try {
                const res = await this.request('/materials/inbounds?per_page=50');
                this.inbounds = res.data.items;
            } catch (error) {
                this.showToastMessage('加载入库记录失败', 'error');
            }
        },

        async loadOutbounds() {
            try {
                const res = await this.request('/materials/outbounds?per_page=50');
                this.outbounds = res.data.items;
            } catch (error) {
                this.showToastMessage('加载出库记录失败', 'error');
            }
        },

        async loadInventory() {
            try {
                const res = await this.request('/materials/inventory');
                this.inventoryItems = res.data.items;
                this.inventoryStats = {
                    total_count: res.data.total_count,
                    total_value: res.data.total_value
                };
            } catch (error) {
                this.showToastMessage('加载库存失败', 'error');
            }
        },

        async loadReportData() {
            await Promise.all([
                this.loadWorkorderStats(),
                this.loadProjectStats(),
                this.loadMaterialStats(),
                this.loadEngineerStats()
            ]);
        },

        async loadWorkorderStats() {
            try {
                const params = new URLSearchParams(this.reportFilters);
                Object.keys(this.reportFilters).forEach(key => {
                    if (!this.reportFilters[key]) params.delete(key);
                });
                const res = await this.request(`/reports/workorder-stats?${params}`);
                this.reportStats = res.data;
            } catch (error) {
                console.error('Load workorder stats error:', error);
            }
        },

        async loadProjectStats() {
            try {
                const res = await this.request('/reports/project-stats');
                this.projectStats = res.data;
            } catch (error) {
                console.error('Load project stats error:', error);
            }
        },

        async loadMaterialStats() {
            try {
                const params = new URLSearchParams(this.reportFilters);
                Object.keys(this.reportFilters).forEach(key => {
                    if (!this.reportFilters[key]) params.delete(key);
                });
                const res = await this.request(`/reports/material-stats?${params}`);
                this.materialStats = res.data;
            } catch (error) {
                console.error('Load material stats error:', error);
            }
        },

        async loadEngineerStats() {
            try {
                const params = new URLSearchParams(this.reportFilters);
                Object.keys(this.reportFilters).forEach(key => {
                    if (!this.reportFilters[key]) params.delete(key);
                });
                const res = await this.request(`/reports/engineer-performance?${params}`);
                this.engineerStats = res.data;
            } catch (error) {
                console.error('Load engineer stats error:', error);
            }
        },

        viewWorkorder(id) {
            this.currentView = 'workorders';
            this.loadWorkorders();
        },

        showWorkorderModal(action, data = null) {
            const isCreate = action === 'create';
            this.modalTitle = isCreate ? '新建工单' : '编辑工单';

            let projectOptions = this.projectList.map(p =>
                `<option value="${p.id}" ${data && data.project_id === p.id ? 'selected' : ''}>${p.name}</option>`
            ).join('');

            this.modalContent = `
                <form @submit.prevent="submitWorkorderForm">
                    <div class="form-group">
                        <label>工单标题 *</label>
                        <input type="text" id="wo-title" value="${data?.title || ''}" required>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>工单类型</label>
                            <select id="wo-type">
                                <option value="maintenance" ${data?.type === 'maintenance' ? 'selected' : ''}>维护</option>
                                <option value="install" ${data?.type === 'install' ? 'selected' : ''}>安装</option>
                                <option value="inspection" ${data?.type === 'inspection' ? 'selected' : ''}>巡检</option>
                                <option value="fault" ${data?.type === 'fault' ? 'selected' : ''}>故障</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>优先级</label>
                            <select id="wo-priority">
                                <option value="normal" ${data?.priority === 'normal' ? 'selected' : ''}>普通</option>
                                <option value="low" ${data?.priority === 'low' ? 'selected' : ''}>低</option>
                                <option value="high" ${data?.priority === 'high' ? 'selected' : ''}>高</option>
                                <option value="urgent" ${data?.priority === 'urgent' ? 'selected' : ''}>紧急</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>所属项目 *</label>
                        <select id="wo-project" required>
                            <option value="">请选择项目</option>
                            ${projectOptions}
                        </select>
                    </div>
                    <div class="form-group">
                        <label>工单描述</label>
                        <textarea id="wo-desc" rows="3">${data?.description || ''}</textarea>
                    </div>
                    <div class="form-actions">
                        <button type="button" @click="closeModal" class="btn-secondary">取消</button>
                        <button type="submit" class="btn-primary">提交</button>
                    </div>
                </form>
            `;
            this.showModal = true;
            this.currentEditData = data;
        },

        async submitWorkorderForm() {
            const title = document.getElementById('wo-title').value;
            const type = document.getElementById('wo-type').value;
            const priority = document.getElementById('wo-priority').value;
            const project_id = parseInt(document.getElementById('wo-project').value);
            const description = document.getElementById('wo-desc').value;

            if (!project_id) {
                this.showToastMessage('请选择项目', 'error');
                return;
            }

            try {
                if (this.currentEditData) {
                    await this.request(`/workorders/${this.currentEditData.id}`, {
                        method: 'PUT',
                        body: JSON.stringify({ title, type, priority, project_id, description })
                    });
                    this.showToastMessage('更新成功', 'success');
                } else {
                    await this.request('/workorders', {
                        method: 'POST',
                        body: JSON.stringify({ title, type, priority, project_id, description })
                    });
                    this.showToastMessage('创建成功', 'success');
                }
                this.closeModal();
                this.loadWorkorders();
                this.loadDashboard();
            } catch (error) {
                this.showToastMessage(error.message || '操作失败', 'error');
            }
        },

        editWorkorder(wo) {
            this.showWorkorderModal('edit', wo);
        },

        viewProject(id) {
            this.currentView = 'workorders';
        },

        showProjectModal(action, data = null) {
            const isCreate = action === 'create';
            this.modalTitle = isCreate ? '新建项目' : '编辑项目';

            this.modalContent = `
                <form @submit.prevent="submitProjectForm">
                    <div class="form-row">
                        <div class="form-group">
                            <label>项目名称 *</label>
                            <input type="text" id="prj-name" value="${data?.name || ''}" required>
                        </div>
                        <div class="form-group">
                            <label>项目代码 *</label>
                            <input type="text" id="prj-code" value="${data?.code || ''}" required>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>客户名称</label>
                        <input type="text" id="prj-customer" value="${data?.customer || ''}">
                    </div>
                    <div class="form-group">
                        <label>项目地址</label>
                        <input type="text" id="prj-address" value="${data?.address || ''}">
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>开始日期</label>
                            <input type="date" id="prj-start" value="${data?.start_date || ''}">
                        </div>
                        <div class="form-group">
                            <label>结束日期</label>
                            <input type="date" id="prj-end" value="${data?.end_date || ''}">
                        </div>
                    </div>
                    <div class="form-group">
                        <label>项目描述</label>
                        <textarea id="prj-desc" rows="3">${data?.description || ''}</textarea>
                    </div>
                    <div class="form-actions">
                        <button type="button" @click="closeModal" class="btn-secondary">取消</button>
                        <button type="submit" class="btn-primary">提交</button>
                    </div>
                </form>
            `;
            this.showModal = true;
            this.currentEditData = data;
        },

        async submitProjectForm() {
            const name = document.getElementById('prj-name').value;
            const code = document.getElementById('prj-code').value;
            const customer = document.getElementById('prj-customer').value;
            const address = document.getElementById('prj-address').value;
            const start_date = document.getElementById('prj-start').value;
            const end_date = document.getElementById('prj-end').value;
            const description = document.getElementById('prj-desc').value;

            try {
                if (this.currentEditData) {
                    await this.request(`/projects/${this.currentEditData.id}`, {
                        method: 'PUT',
                        body: JSON.stringify({ name, code, customer, address, start_date, end_date, description })
                    });
                    this.showToastMessage('更新成功', 'success');
                } else {
                    await this.request('/projects', {
                        method: 'POST',
                        body: JSON.stringify({ name, code, customer, address, start_date, end_date, description })
                    });
                    this.showToastMessage('创建成功', 'success');
                }
                this.closeModal();
                this.loadProjects();
            } catch (error) {
                this.showToastMessage(error.message || '操作失败', 'error');
            }
        },

        viewPoint(pt) {
            console.log('View point:', pt);
        },

        showPointModal(action, data = null) {
            const isCreate = action === 'create';
            this.modalTitle = isCreate ? '新建点位' : '编辑点位';

            let projectOptions = this.projectList.map(p =>
                `<option value="${p.id}" ${data && data.project_id === p.id ? 'selected' : ''}>${p.name}</option>`
            ).join('');

            this.modalContent = `
                <form @submit.prevent="submitPointForm">
                    <div class="form-group">
                        <label>点位名称 *</label>
                        <input type="text" id="pt-name" value="${data?.name || ''}" required>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>点位编码</label>
                            <input type="text" id="pt-code" value="${data?.code || ''}">
                        </div>
                        <div class="form-group">
                            <label>IP地址</label>
                            <input type="text" id="pt-ip" value="${data?.ip_address || ''}">
                        </div>
                    </div>
                    <div class="form-group">
                        <label>所属项目 *</label>
                        <select id="pt-project" required>
                            <option value="">请选择项目</option>
                            ${projectOptions}
                        </select>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>设备型号</label>
                            <input type="text" id="pt-model" value="${data?.device_model || ''}">
                        </div>
                        <div class="form-group">
                            <label>设备序列号</label>
                            <input type="text" id="pt-sn" value="${data?.device_sn || ''}">
                        </div>
                    </div>
                    <div class="form-group">
                        <label>安装地址</label>
                        <input type="text" id="pt-address" value="${data?.address || ''}">
                    </div>
                    <div class="form-actions">
                        <button type="button" @click="closeModal" class="btn-secondary">取消</button>
                        <button type="submit" class="btn-primary">提交</button>
                    </div>
                </form>
            `;
            this.showModal = true;
            this.currentEditData = data;
        },

        async submitPointForm() {
            const name = document.getElementById('pt-name').value;
            const code = document.getElementById('pt-code').value;
            const ip_address = document.getElementById('pt-ip').value;
            const project_id = parseInt(document.getElementById('pt-project').value);
            const device_model = document.getElementById('pt-model').value;
            const device_sn = document.getElementById('pt-sn').value;
            const address = document.getElementById('pt-address').value;

            try {
                if (this.currentEditData) {
                    await this.request(`/points/${this.currentEditData.id}`, {
                        method: 'PUT',
                        body: JSON.stringify({ name, code, ip_address, project_id, device_model, device_sn, address })
                    });
                    this.showToastMessage('更新成功', 'success');
                } else {
                    await this.request('/points', {
                        method: 'POST',
                        body: JSON.stringify({ name, code, ip_address, project_id, device_model, device_sn, address })
                    });
                    this.showToastMessage('创建成功', 'success');
                }
                this.closeModal();
                this.loadPoints();
            } catch (error) {
                this.showToastMessage(error.message || '操作失败', 'error');
            }
        },

        editPoint(pt) {
            this.showPointModal('edit', pt);
        },

        showMaterialModal(action, data = null) {
            const isCreate = action === 'create';
            this.modalTitle = isCreate ? '新建物资' : '编辑物资';

            this.modalContent = `
                <form @submit.prevent="submitMaterialForm">
                    <div class="form-row">
                        <div class="form-group">
                            <label>物资名称 *</label>
                            <input type="text" id="mat-name" value="${data?.name || ''}" required>
                        </div>
                        <div class="form-group">
                            <label>物资编码 *</label>
                            <input type="text" id="mat-code" value="${data?.code || ''}" required ${isCreate ? '' : 'readonly'}>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>分类</label>
                            <input type="text" id="mat-category" value="${data?.category || ''}">
                        </div>
                        <div class="form-group">
                            <label>规格</label>
                            <input type="text" id="mat-spec" value="${data?.spec || ''}">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>单位</label>
                            <input type="text" id="mat-unit" value="${data?.unit || '个'}">
                        </div>
                        <div class="form-group">
                            <label>单价</label>
                            <input type="number" step="0.01" id="mat-price" value="${data?.price || 0}">
                        </div>
                    </div>
                    <div class="form-group">
                        <label>库存预警阈值</label>
                        <input type="number" id="mat-threshold" value="${data?.low_stock_threshold || 10}">
                    </div>
                    <div class="form-actions">
                        <button type="button" @click="closeModal" class="btn-secondary">取消</button>
                        <button type="submit" class="btn-primary">提交</button>
                    </div>
                </form>
            `;
            this.showModal = true;
            this.currentEditData = data;
        },

        async submitMaterialForm() {
            const name = document.getElementById('mat-name').value;
            const code = document.getElementById('mat-code').value;
            const category = document.getElementById('mat-category').value;
            const spec = document.getElementById('mat-spec').value;
            const unit = document.getElementById('mat-unit').value;
            const price = parseFloat(document.getElementById('mat-price').value);
            const low_stock_threshold = parseInt(document.getElementById('mat-threshold').value);

            try {
                if (this.currentEditData) {
                    await this.request(`/materials/${this.currentEditData.id}`, {
                        method: 'PUT',
                        body: JSON.stringify({ name, category, spec, unit, price, low_stock_threshold })
                    });
                    this.showToastMessage('更新成功', 'success');
                } else {
                    await this.request('/materials', {
                        method: 'POST',
                        body: JSON.stringify({ name, code, category, spec, unit, price, low_stock_threshold })
                    });
                    this.showToastMessage('创建成功', 'success');
                }
                this.closeModal();
                this.loadMaterials();
            } catch (error) {
                this.showToastMessage(error.message || '操作失败', 'error');
            }
        },

        editMaterial(m) {
            this.showMaterialModal('edit', m);
        },

        inboundMaterial(m) {
            this.modalTitle = '物资入库';
            this.modalContent = `
                <form @submit.prevent="submitInboundForm">
                    <div class="form-group">
                        <label>物资</label>
                        <input type="text" value="${m.name}" readonly>
                        <input type="hidden" id="inb-material-id" value="${m.id}">
                    </div>
                    <div class="form-group">
                        <label>入库数量 *</label>
                        <input type="number" id="inb-quantity" min="1" required>
                    </div>
                    <div class="form-group">
                        <label>批次号</label>
                        <input type="text" id="inb-batch">
                    </div>
                    <div class="form-group">
                        <label>供应商</label>
                        <input type="text" id="inb-supplier">
                    </div>
                    <div class="form-group">
                        <label>备注</label>
                        <textarea id="inb-remark" rows="2"></textarea>
                    </div>
                    <div class="form-actions">
                        <button type="button" @click="closeModal" class="btn-secondary">取消</button>
                        <button type="submit" class="btn-primary">确认入库</button>
                    </div>
                </form>
            `;
            this.showModal = true;
        },

        async submitInboundForm() {
            const material_id = parseInt(document.getElementById('inb-material-id').value);
            const quantity = parseInt(document.getElementById('inb-quantity').value);
            const batch_no = document.getElementById('inb-batch').value;
            const supplier = document.getElementById('inb-supplier').value;
            const remark = document.getElementById('inb-remark').value;

            try {
                await this.request('/materials/inbound', {
                    method: 'POST',
                    body: JSON.stringify({ material_id, quantity, batch_no, supplier, remark })
                });
                this.showToastMessage('入库成功', 'success');
                this.closeModal();
                this.loadMaterials();
                this.loadInbounds();
            } catch (error) {
                this.showToastMessage(error.message || '入库失败', 'error');
            }
        },

        outboundMaterial(m) {
            this.modalTitle = '物资出库';
            this.modalContent = `
                <form @submit.prevent="submitOutboundForm">
                    <div class="form-group">
                        <label>物资</label>
                        <input type="text" value="${m.name} (当前库存: ${m.current_stock})" readonly>
                        <input type="hidden" id="out-material-id" value="${m.id}">
                    </div>
                    <div class="form-group">
                        <label>出库数量 *</label>
                        <input type="number" id="out-quantity" min="1" max="${m.current_stock}" required>
                    </div>
                    <div class="form-group">
                        <label>关联工单</label>
                        <input type="number" id="out-workorder" placeholder="输入工单ID">
                    </div>
                    <div class="form-group">
                        <label>用途说明</label>
                        <textarea id="out-reason" rows="2" placeholder="出库用途"></textarea>
                    </div>
                    <div class="form-actions">
                        <button type="button" @click="closeModal" class="btn-secondary">取消</button>
                        <button type="submit" class="btn-primary">确认出库</button>
                    </div>
                </form>
            `;
            this.showModal = true;
        },

        async submitOutboundForm() {
            const material_id = parseInt(document.getElementById('out-material-id').value);
            const quantity = parseInt(document.getElementById('out-quantity').value);
            const workorder_id = document.getElementById('out-workorder').value;
            const reason = document.getElementById('out-reason').value;

            try {
                await this.request('/materials/outbound', {
                    method: 'POST',
                    body: JSON.stringify({
                        material_id,
                        quantity,
                        workorder_id: workorder_id ? parseInt(workorder_id) : null,
                        reason
                    })
                });
                this.showToastMessage('出库成功', 'success');
                this.closeModal();
                this.loadMaterials();
                this.loadOutbounds();
            } catch (error) {
                this.showToastMessage(error.message || '出库失败', 'error');
            }
        },

        closeModal() {
            this.showModal = false;
            this.modalTitle = '';
            this.modalContent = '';
            this.currentEditData = null;
        },

        async exportReport() {
            try {
                const params = new URLSearchParams(this.reportFilters);
                Object.keys(this.reportFilters).forEach(key => {
                    if (!this.reportFilters[key]) params.delete(key);
                });

                const response = await fetch(`${API_BASE}/reports/export?${params}`, {
                    headers: {
                        'Authorization': `Bearer ${this.token}`
                    }
                });

                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `工单统计_${new Date().toISOString().split('T')[0]}.xls`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);

                this.showToastMessage('导出成功', 'success');
            } catch (error) {
                this.showToastMessage('导出失败', 'error');
            }
        }
    },

    watch: {
        currentView(newView) {
            if (newView === 'workorders') {
                this.loadWorkorders();
            } else if (newView === 'projects') {
                this.loadProjects();
                this.loadProjectList();
            } else if (newView === 'points') {
                this.loadPoints();
                this.loadProjectList();
            } else if (newView === 'materials') {
                this.loadMaterials();
                this.loadInbounds();
                this.loadOutbounds();
                this.loadInventory();
            } else if (newView === 'reports') {
                this.loadReportData();
                this.loadProjectList();
            }
        },

        materialTab(newTab) {
            if (newTab === 'inbound') {
                this.loadInbounds();
            } else if (newTab === 'outbound') {
                this.loadOutbounds();
            } else if (newTab === 'inventory') {
                this.loadInventory();
            }
        }
    }
});

app.mount('#app');
