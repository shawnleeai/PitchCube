/**
 * PitchCube API 客户端
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class ApiError extends Error {
  constructor(
    public status: number,
    public message: string,
    public data?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

class ApiClient {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        throw new ApiError(
          response.status,
          data?.detail || '请求失败',
          data
        );
      }

      return data as T;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(0, '网络错误，请检查连接');
    }
  }

  // ============ 认证相关 ============

  async login(email: string, password: string) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    return this.request<{
      access_token: string;
      token_type: string;
    }>('/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
    });
  }

  async register(data: {
    email: string;
    username: string;
    password: string;
    confirm_password: string;
  }) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getProfile() {
    return this.request('/users/me');
  }

  async updateProfile(data: {
    full_name?: string;
    company?: string;
    bio?: string;
  }) {
    return this.request('/users/me', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // ============ 产品相关 ============

  async listProducts(skip = 0, limit = 20) {
    return this.request(`/products?skip=${skip}&limit=${limit}`);
  }

  async getProduct(id: string) {
    return this.request(`/products/${id}`);
  }

  async createProduct(data: {
    name: string;
    description: string;
    tagline?: string;
    key_features?: string[];
    target_audience?: string;
    category?: string;
    website_url?: string;
    github_url?: string;
  }) {
    return this.request('/products', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateProduct(id: string, data: Partial<{
    name: string;
    description: string;
    tagline: string;
    key_features: string[];
    target_audience: string;
    category: string;
    website_url: string;
    github_url: string;
  }>) {
    return this.request(`/products/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteProduct(id: string) {
    return this.request(`/products/${id}`, {
      method: 'DELETE',
    });
  }

  async analyzeProduct(id: string) {
    return this.request(`/products/${id}/analyze`);
  }

  async getProductSuggestions(id: string) {
    return this.request(`/products/${id}/suggestions`);
  }

  // ============ 海报相关 ============

  async getPosterTemplates() {
    return this.request('/posters/templates');
  }

  async generatePoster(data: {
    product_name: string;
    product_description: string;
    key_features: string[];
    template_id?: string;
    primary_color?: string;
    size?: string;
  }) {
    return this.request('/posters/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getPosterStatus(id: string) {
    return this.request(`/posters/generations/${id}`);
  }

  async listPosters(skip = 0, limit = 20) {
    return this.request(`/posters/generations?skip=${skip}&limit=${limit}`);
  }

  async enhancePoster(data: {
    product_name: string;
    product_description: string;
    style?: string;
    color_scheme?: string;
    include_text?: boolean;
  }) {
    return this.request('/posters/enhance', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ============ 视频相关 ============

  async getVideoTemplates() {
    return this.request('/videos/templates');
  }

  async generateVideoScript(data: {
    product_name: string;
    product_description: string;
    key_features: string[];
    style?: string;
    duration?: number;
    platform?: string;
  }) {
    return this.request('/videos/generate-script', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async generateVideo(data: {
    product_id: string;
    product_name: string;
    product_description: string;
    key_features: string[];
    script_style?: string;
    target_duration?: number;
    target_platform?: string;
    include_subtitles?: boolean;
    voice_style?: string;
  }) {
    return this.request('/videos/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getVideoStatus(id: string) {
    return this.request(`/videos/generations/${id}`);
  }

  async listVideos(skip = 0, limit = 20) {
    return this.request(`/videos/generations?skip=${skip}&limit=${limit}`);
  }

  // ============ 语音相关 ============

  async getVoices(style?: string, gender?: string) {
    const params = new URLSearchParams();
    if (style) params.append('style', style);
    if (gender) params.append('gender', gender);
    return this.request(`/voice/voices?${params.toString()}`);
  }

  async generateVoice(data: {
    text: string;
    voice_style?: string;
    voice_gender?: string;
    speed?: number;
    use_cache?: boolean;
  }) {
    return this.request('/voice/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getVoiceStatus(id: string) {
    return this.request(`/voice/generations/${id}`);
  }

  async previewVoice(data: { text?: string; voice_id?: string }) {
    return this.request('/voice/preview', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ============ AI 图像相关 ============

  async generateImage(data: {
    prompt: string;
    model?: string;
    size?: string;
    quality?: string;
  }) {
    return this.request('/ai/images/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async generatePosterImage(data: {
    product_name: string;
    product_description: string;
    style?: string;
  }) {
    return this.request('/ai/images/generate-poster', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ============ 角色扮演相关 ============

  async startRoleplay(character: string) {
    return this.request('/ai/roleplay/start', {
      method: 'POST',
      body: JSON.stringify({ character }),
    });
  }

  async sendRoleplayMessage(sessionId: string, message: string) {
    return this.request('/ai/roleplay/chat', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, message }),
    });
  }

  // ============ 支付相关 ============

  async getPlans() {
    return this.request('/payments/plans');
  }

  async createCheckout(planId: string, billingCycle = 'monthly') {
    return this.request('/payments/create-checkout', {
      method: 'POST',
      body: JSON.stringify({ plan_id: planId, billing_cycle: billingCycle }),
    });
  }

  async createAlipayOrder(planId: string, billingCycle = 'monthly') {
    return this.request('/payments/create-alipay-order', {
      method: 'POST',
      body: JSON.stringify({ plan_id: planId, billing_cycle: billingCycle }),
    });
  }

  async getSubscription() {
    return this.request('/payments/subscription');
  }

  async cancelSubscription() {
    return this.request('/payments/cancel', {
      method: 'POST',
    });
  }

  // ============ 健康检查 ============

  async healthCheck() {
    return this.request('/health');
  }

  // ============ 协作空间 ============

  async listProjects(skip = 0, limit = 20) {
    return this.request(`/collab/projects?skip=${skip}&limit=${limit}`);
  }

  async getProject(id: string) {
    return this.request(`/collab/projects/${id}`);
  }

  async createProject(data: {
    name: string;
    description: string;
    project_type: string;
  }) {
    return this.request('/collab/projects', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateProject(id: string, data: Partial<{
    name: string;
    description: string;
    status: string;
  }>) {
    return this.request(`/collab/projects/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteProject(id: string) {
    return this.request(`/collab/projects/${id}`, {
      method: 'DELETE',
    });
  }

  async inviteCollaborator(projectId: string, data: {
    username: string;
    role: string;
  }) {
    return this.request(`/collab/projects/${projectId}/invite`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async removeCollaborator(projectId: string, userId: string) {
    return this.request(`/collab/projects/${projectId}/collaborators/${userId}`, {
      method: 'DELETE',
    });
  }

  async leaveProject(projectId: string) {
    return this.request(`/collab/projects/${projectId}/leave`, {
      method: 'POST',
    });
  }

  // ============ 数据分析 ============

  async getDashboard(timeRange = '7d') {
    return this.request(`/analytics/dashboard?time_range=${timeRange}`);
  }

  async getUserStats() {
    return this.request('/analytics/user-stats');
  }

  async getGenerationStats(period = '7d') {
    return this.request(`/analytics/generations?period=${period}`);
  }

  async getPlatformStats(period = '7d') {
    return this.request(`/analytics/platforms?period=${period}`);
  }

  async trackEvent(eventType: string, data: Record<string, any>) {
    return this.request('/analytics/events', {
      method: 'POST',
      body: JSON.stringify({ event_type: eventType, ...data }),
    });
  }

  // ============ 批量生成 ============

  async batchGenerate(data: {
    product_id: string;
    types: string[];
    options?: Record<string, any>;
  }): Promise<{ batch_id: string; status: string; message: string }> {
    return this.request('/batch/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getBatchStatus(batchId: string) {
    return this.request(`/batch/status/${batchId}`);
  }

  async cancelBatch(batchId: string) {
    return this.request(`/batch/cancel/${batchId}`, {
      method: 'POST',
    });
  }
}

export const apiClient = new ApiClient();
export { ApiError };
