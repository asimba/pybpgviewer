/*******************************************************************************\
This source is subject to the Microsoft Public License.
See http://www.microsoft.com/opensource/licenses.mspx#Ms-PL.
All other rights reserved.

THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, 
EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED 
WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR PURPOSE.
\*******************************************************************************/

#define WIN32_LEAN_AND_MEAN
#include <SDKDDKVer.h>
#include <windows.h>
#include "bpgthumbnailer.h"

// {C5559E6E-5BF1-4F5A-8484-9C2FBC752A10}
const CLSID CLSID_BPGThumbnailProvider={0xc5559e6e,0x5bf1,0x4f5a,{0x84,0x84,0x9c,0x2f,0xbc,0x75,0x2a,0x10}};

HINSTANCE   g_hInst=NULL;
long        g_cDllRef=0;

BOOL APIENTRY DllMain(HMODULE hModule,DWORD dwReason,LPVOID lpReserved){
	switch(dwReason){
	case DLL_PROCESS_ATTACH:
		g_hInst=hModule;
		DisableThreadLibraryCalls(hModule);
		break;
	case DLL_THREAD_ATTACH:
	case DLL_THREAD_DETACH:
	case DLL_PROCESS_DETACH:
		break;
	}
	return TRUE;
}

STDAPI DllGetClassObject(REFCLSID rclsid,REFIID riid,void **ppv){
	HRESULT hr=CLASS_E_CLASSNOTAVAILABLE;
	if(IsEqualCLSID(CLSID_BPGThumbnailProvider,rclsid)){
		hr=E_OUTOFMEMORY;
		ClassFactory *pClassFactory=new ClassFactory();
		if(pClassFactory){
			hr=pClassFactory->QueryInterface(riid,ppv);
			pClassFactory->Release();
		}
	}
	return hr;
}

STDAPI DllCanUnloadNow(void){
	return g_cDllRef>0 ? S_FALSE : S_OK;
}

STDAPI DllRegisterServer(void){
	HRESULT hr;
	wchar_t szModule[MAX_PATH];
	if(GetModuleFileName(g_hInst,szModule,ARRAYSIZE(szModule))==0){
		hr=HRESULT_FROM_WIN32(GetLastError());
		return hr;
	}
	hr=RegisterInprocServer(szModule,CLSID_BPGThumbnailProvider,\
		L"BPGThumbnailProvider",\
		L"Apartment");
	if(SUCCEEDED(hr)){
		hr=RegisterShellExtThumbnailHandler(L".bpg",CLSID_BPGThumbnailProvider);
		if(SUCCEEDED(hr)) SHChangeNotify(SHCNE_ASSOCCHANGED,SHCNF_IDLIST,NULL,NULL);
	}
	return hr;
}

STDAPI DllUnregisterServer(void){
	HRESULT hr=S_OK;
	wchar_t szModule[MAX_PATH];
	if(GetModuleFileName(g_hInst,szModule,ARRAYSIZE(szModule))==0){
		hr=HRESULT_FROM_WIN32(GetLastError());
		return hr;
	}
	hr=UnregisterInprocServer(CLSID_BPGThumbnailProvider);
	if(SUCCEEDED(hr)) hr=UnregisterShellExtThumbnailHandler(L".bpg");
	return hr;
}
