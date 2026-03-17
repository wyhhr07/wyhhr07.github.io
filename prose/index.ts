import { createReader } from "@prose-reader/core"
import { createArchiveFromJszip, Streamer } from "@prose-reader/streamer"
import { from } from "rxjs"
import { loadAsync } from "jszip"

async function createStreamer() {
  /**
   * We create a streamer to load and serve our archive.
   *
   * A streamer is a convenient way to fetch manifest and resources from an archive.
   * This will be used to feed information to the reader.
   *
   * For simplicity we use a web reader but we have a ServiceWorkerStreamer class
   * that can and should be used whenever possible. This will offload the work from
   * the main thread.
   */
  const streamer = new Streamer({
    getArchive: async () => {
      /**
       * First you need to fetch your book. 
       * It can be from anywhere, local, remote, etc.
       */
      const epubResponse = await fetch("../如何阅读西方经典.epub")

      const epubBlob = await epubResponse.blob()

      /**
       * Because epubs are zip archives, we are gonna use jszip to manage them.
       * You could use a different library but we provide helpers to deal with
       * jszip formats as a convenience.
       */
      const epubJszip = await loadAsync(epubBlob)

      /**
       * We are gonna use prose streamer to manage the epub.
       * The streamer work with archives, so we need to create one from the epub.
       *
       * An archive is a higher level interface that is agnostic to the underlying
       * format so the streamer can manage different formats transparently.
       *
       * We do provide several helpers to create archives from different formats.
       * Epubs being zip archives, we have a helper that create an archive from a
       * jszip object.
       */
      const archive = await createArchiveFromJszip(epubJszip)

      return archive
    },
    /**
     * You can configure the streamer to let it know how long it should
     * keep an archive in memory for example. When the archive is no longer available
     * the getArchive callback will be called again.
     */
    cleanArchiveAfter: 5 * 60 * 1000,
  })

  return streamer
}

async function run() {
  const streamer = await createStreamer()

  const manifestResponse = await streamer.fetchManifest({
    /**
     * The streamer is designed to manage several archives that's why
     * it requires a key to be passed to identify which archive to use.
     *
     * In this case we only have one archive so we can use `_` as key.
     */
    key: `_`,
  })

  const manifest = await manifestResponse.json()

  const reader = createReader({
    /**
     * A manifest provide a list of resources and their URIs.
     *
     * However we are loading the epub locally in memory here so the items cannot be
     * fetched directly. This would be possible and encouraged if using a service worker
     * but in our situation we have to hook into the reader to tell him to get its resources
     * from our local streamer directly.
     *
     * This may seems boilerplaty but the separation between the reader and the streamer is what
     * makes prose very flexible and powerful.
     *
     * You can pretty much load anything in any way you want.
     *
     * We tried to create streamers that simplify the friction as much as possible.
     */
    getResource: (item) => {
      return from(streamer.fetchResource({ key: `_`, resourcePath: item.href }))
    },
  })

  /**
   * Finally we can load the reader with our manifest.
   */
  reader.load({
    containerElement: document.getElementById(`app`)!,
    manifest,
  })
}

run()