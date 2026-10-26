# Manual accessibility checklist

## Keyboard

- Tab reaches every interactive element, in a logical order. Shift+Tab goes back.
- The focus is always visible.
- Enter and Space activate buttons and links. Arrow keys work in menus, tabs and lists as expected.
- Escape closes dialogs and menus, and the focus returns to the element that opened them.
- No keyboard trap: the focus can always leave a component.
- A "skip to content" link exists on pages with long navigation.

## Names, roles, states

- Each control has a name that says its purpose ("Delete order ORD-1", not "Click here").
- Images have a text alternative, or are marked as decoration.
- Form fields have labels. Required fields and errors are announced, not only shown in color.
- Expanded, selected, checked and disabled states are exposed.

## Dynamic content

- Error messages, toasts and loading states are announced (live regions).
- A dialog moves the focus into it and keeps the focus there until it closes.
- Page title and main heading change after navigation in a single-page application.

## Visual

- Text contrast at least 4.5:1 (3:1 for large text and for controls).
- Zoom to 200% and a 320 px wide view: no lost content, no horizontal scroll for text.
- No information only by color.
- Motion can be reduced; nothing flashes more than three times per second.

## Screen reader pass (critical journeys)

- Run the journey with a screen reader. The headings, landmarks, names and announcements make sense without the screen.
