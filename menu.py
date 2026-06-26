# menu.py — Right-click context menu (all labels in Norwegian) for MiniKasper

from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QAction, QFont


def build_context_menu(parent, on_follow, on_quote,
                       on_sleep, on_exit) -> QMenu:
    """
    Build and return a Norwegian-labelled context menu.

    Parameters
    ----------
    parent       — the widget that owns the menu
    on_follow    — slot: toggle follow-mouse mode
    on_quote     — slot: show a random speech bubble
    on_sleep     — slot: force the mascot to sleep
    on_exit      — slot: quit the application
    """
    menu = QMenu(parent)

    font = QFont("Segoe UI", 10)
    menu.setFont(font)

    # Style — subtle dark rounded menu
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
        action = QAction(label, parent)
        if checkable:
            action.setCheckable(True)
            action.setChecked(checked)
        action.triggered.connect(slot)
        menu.addAction(action)
        return action

    add("🐾  Følg musa",      on_follow, checkable=True)
    add("💬  Si noe",         on_quote)
    menu.addSeparator()
    add("😴  Sov",            on_sleep)
    menu.addSeparator()
    add("❌  Avslutt",        on_exit)

    return menu