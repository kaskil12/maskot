# menu.py — Right-click context menu (all labels in Norwegian) for MiniKasper

from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QAction, QFont


def build_context_menu(parent, on_follow, on_quote,
                       on_sleep, on_exit) -> QMenu:
    try:
        menu = QMenu(parent)

        font = QFont("Segoe UI", 10)
        menu.setFont(font)

        menu.setStyleSheet("""
            QMenu {
                background-color: #2b2b2b;
                color: #f0f0f0;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 4px 0;
            }
            QMenu::item {
                padding: 6px 18px;
            }
            QMenu::item:selected {
                background-color: #4a90d9;
                border-radius: 4px;
            }
            QMenu::separator {
                height: 1px;
                background: #444;
                margin: 4px 8px;
            }
        """)

        def add(label: str, slot, checkable=False, checked=False) -> QAction:
            try:
                action = QAction(label, parent)

                if checkable:
                    action.setCheckable(True)
                    action.setChecked(checked)

                action.triggered.connect(slot)
                menu.addAction(action)

                return action

            except Exception as e:
                print("build_context_menu.add failed", e)

        add("🐾  Følg musa", on_follow, checkable=True)
        add("💬  Si noe", on_quote)
        menu.addSeparator()
        add("😴  Sov", on_sleep)
        menu.addSeparator()
        add("❌  Avslutt", on_exit)

        return menu

    except Exception as e:
        print("build_context_menu failed", e)
        return QMenu(parent)