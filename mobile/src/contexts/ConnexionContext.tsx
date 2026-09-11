import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface ServerInfo {
  ip: string;
  port: number;
}

interface ConnexionContextType {
  serverInfo: ServerInfo | null;
  isConnected: boolean;
  isConnecting: boolean;
  setServerInfo: (info: ServerInfo | null) => void;
  disconnect: () => void;
  loadSavedConnection: () => Promise<void>;
}

const ConnexionContext = createContext<ConnexionContextType | undefined>(undefined);

const CONNEXION_STORAGE_KEY = 'gestion_stock_connexion';

export function ConnexionProvider({ children }: { children: ReactNode }) {
  const [serverInfo, setServerInfoState] = useState<ServerInfo | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);

  const setServerInfo = (info: ServerInfo | null) => {
    setServerInfoState(info);
    setIsConnected(!!info);
    if (info) {
      AsyncStorage.setItem(CONNEXION_STORAGE_KEY, JSON.stringify(info));
    } else {
      AsyncStorage.removeItem(CONNEXION_STORAGE_KEY);
    }
  };

  const disconnect = () => {
    setServerInfoState(null);
    setIsConnected(false);
    AsyncStorage.removeItem(CONNEXION_STORAGE_KEY);
  };

  const loadSavedConnection = async () => {
    try {
      const saved = await AsyncStorage.getItem(CONNEXION_STORAGE_KEY);
      if (saved) {
        const info = JSON.parse(saved) as ServerInfo;
        setServerInfoState(info);
      }
    } catch (error) {
      console.error('Erreur lors du chargement de la connexion sauvegardée:', error);
    }
  };

  useEffect(() => {
    loadSavedConnection();
  }, []);

  return (
    <ConnexionContext.Provider
      value={{
        serverInfo,
        isConnected,
        isConnecting,
        setServerInfo,
        disconnect,
        loadSavedConnection,
      }}
    >
      {children}
    </ConnexionContext.Provider>
  );
}

export function useConnexion() {
  const context = useContext(ConnexionContext);
  if (context === undefined) {
    throw new Error('useConnexion doit être utilisé dans un ConnexionProvider');
  }
  return context;
}