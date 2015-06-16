/*******************************************************************************\
This source is subject to the Microsoft Public License.
See http://www.microsoft.com/opensource/licenses.mspx#Ms-PL.
All other rights reserved.

THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, 
EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED 
WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR PURPOSE.
\*******************************************************************************/

#pragma once
#include <unknwn.h>
#include <windows.h>
#include <new>
#include <thumbcache.h>
#include <Shlwapi.h>
#include <strsafe.h>
#include <Guiddef.h>
#include <shlobj.h>
#include <bpgdec.h>
#pragma comment(lib,"Shlwapi.lib")
#pragma comment(lib,"bpgdec.lib")

class ClassFactory : public IClassFactory{
	public:
		IFACEMETHODIMP QueryInterface(REFIID riid,void **ppv);
		IFACEMETHODIMP_(ULONG) AddRef();
		IFACEMETHODIMP_(ULONG) Release();
		IFACEMETHODIMP CreateInstance(IUnknown *pUnkOuter,REFIID riid,void **ppv);
		IFACEMETHODIMP LockServer(BOOL fLock);
		ClassFactory();
	protected:
		~ClassFactory();
	private:
		long m_cRef;
};

class BPGThumbnailProvider : public IInitializeWithStream,public IThumbnailProvider{
	public:
		IFACEMETHODIMP QueryInterface(REFIID riid,void **ppv);
		IFACEMETHODIMP_(ULONG) AddRef();
		IFACEMETHODIMP_(ULONG) Release();
		IFACEMETHODIMP Initialize(IStream *pStream,DWORD grfMode);
		IFACEMETHODIMP GetThumbnail(UINT cx,HBITMAP *phbmp,WTS_ALPHATYPE *pdwAlpha);
		BPGThumbnailProvider();
	protected:
		~BPGThumbnailProvider();
	private:
		long m_cRef;
		IStream *m_pStream;
};

HRESULT RegisterInprocServer(PCWSTR pszModule,const CLSID& clsid,PCWSTR pszFriendlyName,PCWSTR pszThreadModel);
HRESULT UnregisterInprocServer(const CLSID& clsid);
HRESULT RegisterShellExtThumbnailHandler(PCWSTR pszFileType,const CLSID& clsid);
HRESULT UnregisterShellExtThumbnailHandler(PCWSTR pszFileType);
