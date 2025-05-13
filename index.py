#!/usr/bin/env python
import qrcode
import api as _
import globals

if __name__ == "__main__":
    print(f"🚀 Server will be running at: {globals.server.url}")

    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(f"{globals.server.url}/")
    qr.make(fit=True)
    qr.print_ascii()

    globals.server.run_server()
