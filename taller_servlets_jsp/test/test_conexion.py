"""
Script de prueba de conexión - Ejecutar en TU OTRO PROYECTO

Este script verifica que:
1. Las credenciales están configuradas correctamente
2. El servidor de Gestión Humana está accesible
3. La autenticación funciona

CÓMO USAR:
----------
1. Copiar este archivo a tu otro proyecto
2. Configurar DJANGO_SETTINGS_MODULE si es necesario
3. Ejecutar: python test_conexion_gh.py
"""

import requests
import json

# ===============================================
# CONFIGURACIÓN - Cambiar según tu proyecto
# ===============================================

GESTION_HUMANA_URL = 'http://127.0.0.1:8000'
CLIENT_ID = 'b1339177-f5f5-40ce-87bc-2526ee72d1a6'
CLIENT_SECRET = '6ef530a6-78ad-4810-9191-391243b3bf2d'

# ===============================================
# NO MODIFICAR DEBAJO DE ESTA LÍNEA
# ===============================================

def test_conexion():
    """Test de conexión al microservicio"""
    
    print("="*60)
    print("🔍 TEST DE CONEXIÓN A GESTIÓN HUMANA")
    print("="*60 + "\n")
    
    # Test 1: Servidor accesible
    print("1️⃣  Verificando que el servidor esté corriendo...")
    try:
        response = requests.get(f"{GESTION_HUMANA_URL}/microservice/", timeout=5)
        print(f"   ✓ Servidor responde (Status: {response.status_code})\n")
    except requests.exceptions.ConnectionError:
        print("   ✗ ERROR: No se puede conectar")
        print(f"   ¿Está corriendo el servidor en {GESTION_HUMANA_URL}?")
        print("   Verifica con: python manage.py runserver\n")
        return False
    except Exception as e:
        print(f"   ✗ Error inesperado: {e}\n")
        return False
    
    # Test 2: Autenticación
    print("2️⃣  Probando autenticación de aplicación...")
    auth_url = f"{GESTION_HUMANA_URL}/microservice/api-apps/authenticate/"
    
    try:
        response = requests.post(
            auth_url,
            json={
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET
            },
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Autenticación exitosa")
            print(f"   Token: {data.get('access_token', 'N/A')[:30]}...")
            print(f"   Expira en: {data.get('expires_in', 'N/A')} segundos\n")
        else:
            print(f"   ✗ Error autenticación: {response.status_code}")
            print(f"   Respuesta: {response.text}\n")
            return False
            
    except Exception as e:
        print(f"   ✗ Error: {e}\n")
        return False
    
    # Test 3: Endpoint bulk
    print("3️⃣  Probando endpoint de sincronización bulk...")
    bulk_url = f"{GESTION_HUMANA_URL}/microservice/api-sync/pull/bulk/"
    headers = {
        'X-Client-ID': CLIENT_ID,
        'X-Client-Secret': CLIENT_SECRET,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            bulk_url,
            json={'solo_activos': True},
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            total = data.get('total', 0)
            print(f"   ✓ Endpoint bulk funciona")
            print(f"   Total usuarios disponibles: {total}")
            
            if total > 0:
                print(f"   Usuarios:")
                for user in data.get('usuarios', [])[:3]:
                    print(f"     - {user.get('username')} ({user.get('email')})")
                if total > 3:
                    print(f"     ... y {total - 3} más")
            print()
        else:
            print(f"   ✗ Error: {response.status_code}")
            print(f"   Respuesta: {response.text}\n")
            return False
            
    except Exception as e:
        print(f"   ✗ Error: {e}\n")
        return False
    
    # Resumen
    print("="*60)
    print("✅ TODOS LOS TESTS PASARON")
    print("="*60)
    print("\n🎯 Siguiente paso:")
    print("   python manage.py sync_usuarios_inicial")
    print()
    
    return True


if __name__ == '__main__':
    exito = test_conexion()
    exit(0 if exito else 1)
