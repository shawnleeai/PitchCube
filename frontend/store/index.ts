/**
 * Zustand Store for PitchCube Global State
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  avatar_url?: string;
  role: string;
  is_verified: boolean;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  login: (user: User, token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      
      setToken: (token) => set({ token, isAuthenticated: !!token }),
      
      login: (user, token) => set({
        user,
        token,
        isAuthenticated: true,
      }),
      
      logout: () => set({
        user: null,
        token: null,
        isAuthenticated: false,
      }),
    }),
    {
      name: 'pitchcube-auth',
    }
  )
);

interface Product {
  id: string;
  name: string;
  description: string;
  tagline?: string;
  key_features: string[];
  poster_count: number;
  video_count: number;
  created_at: string;
}

interface ProductState {
  currentProduct: Product | null;
  products: Product[];
  setCurrentProduct: (product: Product | null) => void;
  setProducts: (products: Product[]) => void;
  addProduct: (product: Product) => void;
  updateProduct: (id: string, data: Partial<Product>) => void;
  removeProduct: (id: string) => void;
}

export const useProductStore = create<ProductState>((set) => ({
  currentProduct: null,
  products: [],
  
  setCurrentProduct: (product) => set({ currentProduct: product }),
  
  setProducts: (products) => set({ products }),
  
  addProduct: (product) => set((state) => ({
    products: [product, ...state.products],
  })),
  
  updateProduct: (id, data) => set((state) => ({
    products: state.products.map((p) =>
      p.id === id ? { ...p, ...data } : p
    ),
    currentProduct: state.currentProduct?.id === id
      ? { ...state.currentProduct, ...data }
      : state.currentProduct,
  })),
  
  removeProduct: (id) => set((state) => ({
    products: state.products.filter((p) => p.id !== id),
    currentProduct: state.currentProduct?.id === id ? null : state.currentProduct,
  })),
}));

interface UIState {
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
  toggleTheme: () => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarOpen: true,
      theme: 'light',
      
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      
      setTheme: (theme) => set({ theme }),
      
      toggleTheme: () => set((state) => ({
        theme: state.theme === 'light' ? 'dark' : 'light',
      })),
    }),
    {
      name: 'pitchcube-ui',
    }
  )
);

interface GenerationState {
  currentPosterId: string | null;
  currentVideoId: string | null;
  currentVoiceId: string | null;
  setCurrentPosterId: (id: string | null) => void;
  setCurrentVideoId: (id: string | null) => void;
  setCurrentVoiceId: (id: string | null) => void;
  clearGenerationIds: () => void;
}

export const useGenerationStore = create<GenerationState>((set) => ({
  currentPosterId: null,
  currentVideoId: null,
  currentVoiceId: null,
  
  setCurrentPosterId: (id) => set({ currentPosterId: id }),
  setCurrentVideoId: (id) => set({ currentVideoId: id }),
  setCurrentVoiceId: (id) => set({ currentVoiceId: id }),
  
  clearGenerationIds: () => set({
    currentPosterId: null,
    currentVideoId: null,
    currentVoiceId: null,
  }),
}));
