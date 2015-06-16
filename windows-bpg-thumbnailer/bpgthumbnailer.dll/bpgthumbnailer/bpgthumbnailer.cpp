/*******************************************************************************\
This source is subject to the Microsoft Public License.
See http://www.microsoft.com/opensource/licenses.mspx#Ms-PL.
All other rights reserved.

THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, 
EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED 
WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR PURPOSE.
\*******************************************************************************/

#include "bpgthumbnailer.h"

extern long g_cDllRef;
extern HINSTANCE g_hInst;

ClassFactory::ClassFactory():m_cRef(1){
	InterlockedIncrement(&g_cDllRef);
}

ClassFactory::~ClassFactory(){
	InterlockedDecrement(&g_cDllRef);
}

IFACEMETHODIMP ClassFactory::QueryInterface(REFIID riid,void **ppv){
	static const QITAB qit[]={QITABENT(ClassFactory,IClassFactory),{0},};
	return QISearch(this,qit,riid,ppv);
}

IFACEMETHODIMP_(ULONG) ClassFactory::AddRef(){
	return InterlockedIncrement(&m_cRef);
}

IFACEMETHODIMP_(ULONG) ClassFactory::Release(){
	ULONG cRef=InterlockedDecrement(&m_cRef);
	if(cRef==0) delete this;
	return cRef;
}

IFACEMETHODIMP ClassFactory::CreateInstance(IUnknown *pUnkOuter,REFIID riid,void **ppv){
	HRESULT hr=CLASS_E_NOAGGREGATION;
	if(pUnkOuter==NULL){
		hr=E_OUTOFMEMORY;
		BPGThumbnailProvider *pExt=new (std::nothrow) BPGThumbnailProvider();
		if(pExt){
			hr=pExt->QueryInterface(riid,ppv);
			pExt->Release();
		}
	}
	return hr;
}

IFACEMETHODIMP ClassFactory::LockServer(BOOL fLock){
	if(fLock) InterlockedIncrement(&g_cDllRef);
	else InterlockedDecrement(&g_cDllRef);
	return S_OK;
}

BPGThumbnailProvider::BPGThumbnailProvider() : m_cRef(1),m_pStream(NULL){
	InterlockedIncrement(&g_cDllRef);
}

BPGThumbnailProvider::~BPGThumbnailProvider(){
	InterlockedDecrement(&g_cDllRef);
}

#pragma region IUnknown

IFACEMETHODIMP BPGThumbnailProvider::QueryInterface(REFIID riid,void **ppv){
	static const QITAB qit[]={QITABENT(BPGThumbnailProvider,IThumbnailProvider),\
		QITABENT(BPGThumbnailProvider,IInitializeWithStream),{0},};
	return QISearch(this,qit,riid,ppv);
}

IFACEMETHODIMP_(ULONG) BPGThumbnailProvider::AddRef(){
	return InterlockedIncrement(&m_cRef);
}

IFACEMETHODIMP_(ULONG) BPGThumbnailProvider::Release(){
	ULONG cRef=InterlockedDecrement(&m_cRef);
	if (cRef==0) delete this;
	return cRef;
}

#pragma endregion

#pragma region IInitializeWithStream

IFACEMETHODIMP BPGThumbnailProvider::Initialize(IStream *pStream,DWORD grfMode){
	HRESULT hr=HRESULT_FROM_WIN32(ERROR_ALREADY_INITIALIZED);
	if(m_pStream==NULL)	hr=pStream->QueryInterface(&m_pStream);
	return hr;
}

#pragma endregion

#pragma region IThumbnailProvider

IFACEMETHODIMP BPGThumbnailProvider::GetThumbnail(UINT cx,HBITMAP *phbmp,WTS_ALPHATYPE *pdwAlpha){
	*phbmp=NULL;
	*pdwAlpha=WTSAT_UNKNOWN;
	ULONG bsize=0,rsize=0;
	char *buffer=(char*)malloc(8192),*bpntr=buffer;
	if(buffer==NULL) return E_FAIL;
	HRESULT rflag=S_OK;
	LARGE_INTEGER dw;
	dw.QuadPart=0;
	m_pStream->Seek(dw,STREAM_SEEK_SET,0);
	while (true){
		rflag=m_pStream->Read(bpntr,8192,&rsize);
		if(rsize){
			bsize+=rsize;
			bpntr=(char *)realloc(buffer,bsize+8192);
			if(bpntr){
				buffer=bpntr;
				bpntr+=bsize*sizeof(char);
			}
			else{
				free(buffer);
				return E_FAIL;
			}
		}
		else{
			if(rflag==S_FALSE) break;
		}
	}
	int w=0,h=0;
	if(bpgdec_buffer_getwh(buffer,bsize,w,h)){
		char *imgbuffer=new char[w*h*4];
		if (imgbuffer){
			if(bpgdec_buffer(buffer,bsize,imgbuffer,w,h)){
				int k=w*h*3-1,s=w*h-1;
				unsigned char swp[4];
				swp[3]=0;
				while(k>0){
					swp[0]=imgbuffer[k--];
					swp[1]=imgbuffer[k--];
					swp[2]=imgbuffer[k--];
					((int *)imgbuffer)[s--]=*(int *)swp;
				}
				*phbmp=(HBITMAP)CreateBitmap(w,h,1,32,(BYTE *)imgbuffer);
			}
			delete imgbuffer;
			rflag=NOERROR;
		}
		else rflag=E_FAIL;
	}
	else rflag=E_FAIL;
	free(buffer);
	return rflag;
}

#pragma endregion

#pragma region RegistryHelperFunctions

HRESULT SetHKCRRegistryKeyAndValue(PCWSTR pszSubKey,PCWSTR pszValueName,PCWSTR pszData){
	HRESULT hr;
	HKEY hKey=NULL;
	hr=HRESULT_FROM_WIN32(RegCreateKeyEx(HKEY_CLASSES_ROOT,pszSubKey,0,NULL,REG_OPTION_NON_VOLATILE,KEY_WRITE,NULL,&hKey,NULL));
	if(SUCCEEDED(hr)){
		if(pszData){
			DWORD cbData=lstrlen(pszData)*sizeof(*pszData);
			hr=HRESULT_FROM_WIN32(RegSetValueEx(hKey,pszValueName,0,REG_SZ,reinterpret_cast<const BYTE *>(pszData),cbData));
		}
		RegCloseKey(hKey);
	}
	return hr;
}

HRESULT GetHKCRRegistryKeyAndValue(PCWSTR pszSubKey,PCWSTR pszValueName,PWSTR pszData,DWORD cbData){
	HRESULT hr;
	HKEY hKey=NULL;
	hr=HRESULT_FROM_WIN32(RegOpenKeyEx(HKEY_CLASSES_ROOT,pszSubKey,0,KEY_READ,&hKey));
	if(SUCCEEDED(hr)){
		hr=HRESULT_FROM_WIN32(RegQueryValueEx(hKey,pszValueName,NULL,NULL,reinterpret_cast<LPBYTE>(pszData),&cbData));
		RegCloseKey(hKey);
	}
	return hr;
}

#pragma endregion

HRESULT RegisterInprocServer(PCWSTR pszModule,const CLSID& clsid,PCWSTR pszFriendlyName,PCWSTR pszThreadModel){
	if(pszModule==NULL || pszThreadModel==NULL) return E_INVALIDARG;
	HRESULT hr;
	wchar_t szCLSID[MAX_PATH];
	StringFromGUID2(clsid,szCLSID,ARRAYSIZE(szCLSID));
	wchar_t szSubkey[MAX_PATH];
	hr=StringCchPrintf(szSubkey,ARRAYSIZE(szSubkey),L"CLSID\\%s",szCLSID);
	if(SUCCEEDED(hr)){
		hr=SetHKCRRegistryKeyAndValue(szSubkey,NULL,pszFriendlyName);
		if(SUCCEEDED(hr)){
			hr=StringCchPrintf(szSubkey,ARRAYSIZE(szSubkey),L"CLSID\\%s\\InprocServer32",szCLSID);
			if(SUCCEEDED(hr)){
				hr=SetHKCRRegistryKeyAndValue(szSubkey,NULL,pszModule);
				if(SUCCEEDED(hr)) hr=SetHKCRRegistryKeyAndValue(szSubkey,L"ThreadingModel",pszThreadModel);
			}
		}
	}
	return hr;
}

HRESULT UnregisterInprocServer(const CLSID& clsid){
	HRESULT hr=S_OK;
	wchar_t szCLSID[MAX_PATH];
	StringFromGUID2(clsid,szCLSID,ARRAYSIZE(szCLSID));
	wchar_t szSubkey[MAX_PATH];
	hr=StringCchPrintf(szSubkey,ARRAYSIZE(szSubkey),L"CLSID\\%s",szCLSID);
	if(SUCCEEDED(hr)) hr=HRESULT_FROM_WIN32(RegDeleteTree(HKEY_CLASSES_ROOT,szSubkey));
	return hr;
}

HRESULT RegisterShellExtThumbnailHandler(PCWSTR pszFileType,const CLSID& clsid){
	if(pszFileType==NULL) return E_INVALIDARG;
	HRESULT hr;
	wchar_t szCLSID[MAX_PATH];
	StringFromGUID2(clsid,szCLSID,ARRAYSIZE(szCLSID));
	wchar_t szSubkey[MAX_PATH];
	if(*pszFileType==L'.'){
		wchar_t szDefaultVal[260];
		hr=GetHKCRRegistryKeyAndValue(pszFileType,NULL,szDefaultVal,sizeof(szDefaultVal));
		if(SUCCEEDED(hr) && szDefaultVal[0]!=L'\0')	pszFileType=szDefaultVal;
	}
	hr=StringCchPrintf(szSubkey,ARRAYSIZE(szSubkey),L"%s\\shellex\\{E357FCCD-A995-4576-B01F-234630154E96}",pszFileType);
	if(SUCCEEDED(hr)) hr=SetHKCRRegistryKeyAndValue(szSubkey,NULL,szCLSID);
	return hr;
}

HRESULT UnregisterShellExtThumbnailHandler(PCWSTR pszFileType){
	if(pszFileType==NULL) return E_INVALIDARG;
	HRESULT hr;
	wchar_t szSubkey[MAX_PATH];
	if(*pszFileType==L'.'){
		wchar_t szDefaultVal[260];
		hr=GetHKCRRegistryKeyAndValue(pszFileType,NULL,szDefaultVal,sizeof(szDefaultVal));
		if(SUCCEEDED(hr) && szDefaultVal[0]!=L'\0') pszFileType=szDefaultVal;
	}
	hr=StringCchPrintf(szSubkey,ARRAYSIZE(szSubkey),L"%s\\shellex\\{E357FCCD-A995-4576-B01F-234630154E96}",pszFileType);
	if(SUCCEEDED(hr)) hr=HRESULT_FROM_WIN32(RegDeleteTree(HKEY_CLASSES_ROOT,szSubkey));
	return hr;
}
