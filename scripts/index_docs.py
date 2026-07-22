"""
CLI para indexar PDFs del cliente en ChromaDB.

Uso:
  python scripts/index_docs.py --status
  python scripts/index_docs.py --asignatura circuitos
  python scripts/index_docs.py --all
  python scripts/index_docs.py --asignatura circuitos --force
  python scripts/index_docs.py --all --force
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.indexer import chroma_status, index_all, index_asignatura


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Indexador de documentos — Tutor RAG · Ingeniería Eléctrica"
    )
    parser.add_argument(
        "--asignatura",
        help="ID de asignatura: circuitos | electronica | maquinas_electricas",
    )
    parser.add_argument(
        "--all", action="store_true", help="Indexar todas las asignaturas"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reindexar desde cero (borra colección existente)",
    )
    parser.add_argument(
        "--status", action="store_true", help="Ver estado actual de ChromaDB"
    )
    args = parser.parse_args()

    if args.status:
        print("\n📊 Estado de ChromaDB:")
        for asig, n in chroma_status().items():
            icon = "✅" if n > 0 else "⚪"
            print(f"  {icon}  {asig}: {n} chunks indexados")
        print()

    elif args.all:
        force_txt = " (reindexando desde cero)" if args.force else ""
        print(f"\n🔄 Indexando todas las asignaturas{force_txt}...")
        for asig, resultado in index_all(force=args.force).items():
            icon = "✅" if isinstance(resultado, int) else "⚠️ "
            print(f"  {icon}  {asig}: {resultado}")
        print()

    elif args.asignatura:
        force_txt = " (reindexando desde cero)" if args.force else ""
        print(f"\n🔄 Indexando '{args.asignatura}'{force_txt}...")
        try:
            n = index_asignatura(args.asignatura, force=args.force)
            print(f"  ✅  {args.asignatura}: {n} chunks indexados\n")
        except (FileNotFoundError, ValueError) as exc:
            print(f"  ❌  Error: {exc}\n")
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
