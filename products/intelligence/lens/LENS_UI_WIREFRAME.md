Symbolic Lens - No-Code Editor Wireframe
I. Layout
The UI is a single-page application divided into three main columns and a top header.

+----------------------------------------------------------------------------------+
| [LOGO] Symbolic Lens   | [Translate File] [Design Photon] [Preview] [Publish]  |  [User: ΛiD]
+----------------------------------------------------------------------------------+
| [PALETTE]              | [CANVAS]                                               | [INSPECTOR]
|                        |                                                        |
| Widgets:               | Drag and drop widgets and GLYPHs here.                 | Properties for Selected Item:
| - MetricCard           |                                                        | (Form generated from schema)
| - BarCompare           | Arrange, connect, and resize.                          |
| - ForceGraph           |                                                        | -----------------------------
|                        |                                                        | Title: [__________________]
| GLYPHs:                |                                                        |
| - Topic                |                                                        | Data Binding:
| - Person               |                                                        | [Type: Static ▼]
| - Organization         |                                                        | [Value: _______________]
|                        |                                                        |
| Data Bindings:         |                                                        | Access Tag: [____________]
| - (From Source File)   |                                                        |
+----------------------------------------------------------------------------------+

II. Panels
Header:

Mode Switch: Radio buttons to switch between workflows: Translate File, Design Photon, Preview.

Publish Button: Becomes active when in Design/Preview mode. Triggers ΛiD checks before publishing.

Left Panel (Palette):

A searchable, accordion-style list of available items to drag onto the canvas.

Widgets: Populated from GET /lens/presets. Shows items like MetricCard, TableView.

GLYPHs: Standard symbolic types like Topic, Person, Concept.

Data Bindings: When a file has been translated, this section lists discovered entities (e.g., functions, data columns) that can be bound to widget properties.

Center Panel (Canvas):

The main interactive area where the Photon is built.

Supports drag, drop, resize, and selection of nodes.

Supports drawing edges between nodes to create relationships.

State: Initially shows a "Drop a file to start" prompt when in Translate File mode. In Design Photon mode, it's the authoring surface.

Right Panel (Inspector):

Context-aware: Displays properties for the currently selected item on the canvas (a widget, a GLYPH, or the Photon document itself).

Schema-Driven: The form fields displayed are dynamically rendered from the properties_schema (for widgets) or the photon.schema.json (for document settings like Title). This is the core of the no-code experience.

III. User Flows
Translate a File:

User selects Translate File mode.

Canvas shows a drop zone. User drops report.pdf.

A modal appears: "Choose Translation Profile: [Safe (Default)] [Balanced] [Full Analysis (Requires ΛiD Consent)]".

User clicks "Translate". A job is sent to POST /lens/jobs.

A progress indicator is shown. On completion, the Canvas is populated with the resulting GLYPHs and suggested widgets. The "Palette -> Data Bindings" section is filled.

The user is prompted to "Switch to Design Mode to customize".

Design a Photon:

User selects Design Photon mode.

User drags a MetricCard from the Palette onto the Canvas. A new card appears.

User clicks the new card. The Inspector on the right populates with fields: "Title", "Value", "Unit", "Change", etc., as defined in the widget's schema.

User types "Total Revenue" into the Title field. The card on the canvas updates in real-time.

User drags a data binding (e.g., sales.csv -> total_revenue) from the Palette onto the "Value" field in the Inspector, creating a live link.

Publish:

User clicks Publish.

The system calls POST /lens/photon/validate with the current Photon JSON.

If valid, it performs a final ΛiD check based on access_tag properties.

If authorized, it sends the final document to POST /lens/photon/publish. A shareable link is provided.

