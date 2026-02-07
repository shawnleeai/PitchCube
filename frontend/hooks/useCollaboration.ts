/**
 * WebSocket Hook for Real-time Collaboration
 */

import { useState, useEffect, useCallback, useRef } from 'react';

interface UseCollaborationOptions {
  roomId: string;
  userId: string;
  autoConnect?: boolean;
}

interface CursorPosition {
  x: number;
  y: number;
  element?: string;
}

interface Collaborator {
  odify: string;
  cursor?: CursorPosition;
  color?: string;
}

export function useCollaboration({
  roomId,
  userId,
  autoConnect = true,
}: UseCollaborationOptions) {
  const [isConnected, setIsConnected] = useState(false);
  const [collaborators, setCollaborators] = useState<Record<string, Collaborator>>({});
  const [cursors, setCursors] = useState<Record<string, CursorPosition>>({});
  const [documentState, setDocumentState] = useState<Record<string, any>>({});
  const [error, setError] = useState<string | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (typeof window === 'undefined') return;
    
    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}/ws/collab/${roomId}?user_id=${userId}`;
    
    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;
      
      ws.onopen = () => {
        setIsConnected(true);
        setError(null);
      };
      
      ws.onclose = () => {
        setIsConnected(false);
      };
      
      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        setError('连接错误');
      };
      
      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          handleMessage(message);
        } catch (e) {
          console.error('Failed to parse message:', e);
        }
      };
    } catch (e) {
      setError('无法建立连接');
    }
  }, [roomId, userId]);

  const handleMessage = useCallback((message: any) => {
    switch (message.type) {
      case 'user_joined':
        setCollaborators((prev) => ({
          ...prev,
          [message.user_id]: { odify: message.user_id },
        }));
        break;
      
      case 'cursor_update':
        setCursors(message.cursors);
        break;
      
      case 'content_changed':
        setDocumentState((prev) => ({
          ...prev,
          ...message.changes,
        }));
        break;
      
      case 'state_sync':
        setDocumentState(message.state);
        setCursors(message.cursors);
        break;
      
      case 'region_locked':
        setDocumentState((prev) => ({
          ...prev,
          lockedRegions: {
            ...(prev.lockedRegions || {}),
            [message.region_id]: message.locked_by,
          },
        }));
        break;
      
      case 'region_unlocked':
        setDocumentState((prev) => {
          const lockedRegions = { ...(prev.lockedRegions || {}) };
          delete lockedRegions[message.region_id];
          return { ...prev, lockedRegions };
        });
        break;
    }
  }, []);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    setIsConnected(false);
  }, []);

  const sendMessage = useCallback((type: string, data: any = {}) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type, ...data }));
    }
  }, []);

  const sendCursorMove = useCallback((position: CursorPosition) => {
    sendMessage('cursor_move', position);
  }, [sendMessage]);

  const sendContentUpdate = useCallback((changes: Record<string, any>) => {
    sendMessage('content_update', { changes });
  }, [sendMessage]);

  const lockRegion = useCallback((regionId: string) => {
    sendMessage('lock_region', { region_id: regionId });
  }, [sendMessage]);

  const unlockRegion = useCallback((regionId: string) => {
    sendMessage('unlock_region', { region_id: regionId });
  }, [sendMessage]);

  const requestStateSync = useCallback(() => {
    sendMessage('get_state');
  }, [sendMessage]);

  useEffect(() => {
    if (autoConnect) {
      connect();
    }
    
    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  return {
    isConnected,
    collaborators,
    cursors,
    documentState,
    error,
    connect,
    disconnect,
    sendCursorMove,
    sendContentUpdate,
    lockRegion,
    unlockRegion,
    requestStateSync,
  };
}
