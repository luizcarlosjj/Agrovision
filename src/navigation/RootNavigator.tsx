/**
 * Root Navigator
 * Main navigation structure with Bottom Tab Navigator
 */

import React from 'react';
import { Text } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import {
  HomeScreen,
  CameraScreen,
  ProcessingScreen,
  ResultScreen,
  AuditarModeloScreen,
  InstitutionalScreen,
  CategoryScreen,
  ArticleScreen,
  TestModeScreen,
  HistoryScreen,
} from '@screens';
import { RootStackParamList } from './types';
import { COLORS } from '@utils/constants';

/**
 * Create navigators
 */
const Stack = createNativeStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator<RootStackParamList>();

/**
 * Analysis Stack Navigator
 */
function AnalysisNavigator() {
  return (
    <Stack.Navigator
      initialRouteName="Home"
      screenOptions={{
        headerShown: false,
        cardStyle: {
          backgroundColor: COLORS.BACKGROUND,
        },
        animationEnabled: true,
      }}
    >
      <Stack.Screen
        name="Home"
        component={HomeScreen}
        options={{
          title: 'AgroVision',
        }}
      />

      <Stack.Screen
        name="Camera"
        component={CameraScreen}
        options={{
          title: 'Capturar Imagem',
          animationEnabled: true,
        }}
      />

      <Stack.Screen
        name="Processing"
        component={ProcessingScreen}
        options={{
          title: 'Processando',
          animationEnabled: false,
          gestureEnabled: false,
        }}
      />

      <Stack.Screen
        name="Result"
        component={ResultScreen}
        options={{
          title: 'Resultado',
          animationEnabled: true,
        }}
      />

      <Stack.Screen
        name="AuditarModelo"
        component={AuditarModeloScreen}
        options={{
          title: 'Auditar Modelo',
          animationEnabled: true,
        }}
      />

      <Stack.Screen
        name="TestMode"
        component={TestModeScreen}
        options={{
          title: 'Modo Científico (lote)',
        }}
      />
    </Stack.Navigator>
  );
}

function HistoryNavigator() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
        cardStyle: { backgroundColor: COLORS.BACKGROUND },
      }}
    >
      <Stack.Screen name="History" component={HistoryScreen} />
    </Stack.Navigator>
  );
}


/**
 * Institutional Stack Navigator
 */
function InstitutionalNavigator() {
  return (
    <Stack.Navigator
      initialRouteName="InstitutionalHome"
      screenOptions={{
        headerShown: false,
        cardStyle: {
          backgroundColor: COLORS.BACKGROUND,
        },
        animationEnabled: true,
      }}
    >
      <Stack.Screen
        name="InstitutionalHome"
        component={InstitutionalScreen}
        options={{
          title: 'Biblioteca Agronômica',
        }}
      />

      <Stack.Screen
        name="InstitutionalCategory"
        component={CategoryScreen}
        options={{
          title: 'Categoria',
          animationEnabled: true,
        }}
      />

      <Stack.Screen
        name="InstitutionalArticle"
        component={ArticleScreen}
        options={{
          title: 'Artigo',
          animationEnabled: true,
        }}
      />
    </Stack.Navigator>
  );
}

/**
 * Root navigator component with Bottom Tabs
 */
export function RootNavigator() {
  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={{
          headerShown: false,
          tabBarActiveTintColor: COLORS.PRIMARY,
          tabBarInactiveTintColor: COLORS.TEXT_SECONDARY,
          tabBarStyle: {
            backgroundColor: COLORS.BACKGROUND,
            borderTopColor: COLORS.BORDER,
            borderTopWidth: 1,
          },
        }}
      >
        <Tab.Screen
          name="AnalysisTab"
          component={AnalysisNavigator}
          options={{
            title: 'Análise',
            tabBarLabel: 'Análise',
            tabBarIcon: ({ color }) => <Text style={{ color, fontSize: 20 }}>🌾</Text>,
          }}
          listeners={({ navigation }) => ({
            tabPress: (e) => {
              e.preventDefault();
              navigation.navigate('Home');
            },
          })}
        />

        <Tab.Screen
          name="HistoryTab"
          component={HistoryNavigator}
          options={{
            title: 'Histórico',
            tabBarLabel: 'Histórico',
            tabBarIcon: ({ color }) => <Text style={{ color, fontSize: 20 }}>📋</Text>,
          }}
        />

        <Tab.Screen
          name="Institutional"
          component={InstitutionalNavigator}
          options={{
            title: 'Institucional',
            tabBarLabel: 'Institucional',
            tabBarIcon: ({ color }) => <Text style={{ color, fontSize: 20 }}>📚</Text>,
          }}
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
}
